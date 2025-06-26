"""
Dépendances FastAPI pour l'application.
"""
from __future__ import annotations
from typing import Generator, Optional, Union, AsyncGenerator, TYPE_CHECKING, Any

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.api.audiobookshelf import AudiobookshelfClient
from app.db import get_db, get_async_db, AsyncSessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token

# Import différé pour éviter les imports circulaires
if TYPE_CHECKING:
    from app.db.models.base import User
    from app import crud, models

# Schéma OAuth2 pour l'authentification par token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db_session() -> Generator[Session, None, None]:
    """
    Fournit une session de base de données synchrone.
    
    À utiliser pour la rétrocompatibilité.
    Préférez l'utilisation directe de `get_db` pour les nouvelles implémentations.
    """
    return get_db()


def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fournit une session de base de données asynchrone.
    
    À utiliser pour les opérations asynchrones.
    """
    return get_async_db()


def get_audiobookshelf_client() -> AudiobookshelfClient:
    """
    Fournit une instance du client Audiobookshelf.
    
    Returns:
        AudiobookshelfClient: Une instance configurée du client
        
    Raises:
        HTTPException: Si la configuration est manquante
    """
    if not all([settings.ABS_API_URL, settings.ABS_USERNAME, settings.ABS_PASSWORD]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration Audiobookshelf manquante"
        )
    
    return AudiobookshelfClient(
        base_url=settings.ABS_API_URL,
        username=settings.ABS_USERNAME,
        password=settings.ABS_PASSWORD
    )


async def get_current_user(
    db: AsyncSession = Depends(get_async_db), 
    token: str = Depends(oauth2_scheme)
) -> 'models.User':
    """
    Récupère l'utilisateur actuellement authentifié.
    
    Args:
        db: Session de base de données
        token: JWT token d'authentification
        
    Returns:
        User: L'utilisateur authentifié
        
    Raises:
        HTTPException: Si l'authentification échoue
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
        
    # Utilisation de la session asynchrone
    user = await crud.crud_user.get_user_by_username(db, username=username)
    if user is None:
        await db.close()
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: 'models.User' = Depends(get_current_user),
) -> 'models.User':
    """
    Vérifie que l'utilisateur actuel est actif.
    """
    if not crud.crud_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user


async def get_current_active_superuser(
    current_user: 'models.User' = Depends(get_current_user),
) -> 'models.User':
    """
    Vérifie que l'utilisateur actuel est un superutilisateur.
    """
    if not crud.crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, 
            detail="L'utilisateur n'a pas les privilèges suffisants"
        )
    return current_user
