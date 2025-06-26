"""
Dépendances communes pour les routes API.

Ce module fournit des dépendances réutilisables pour les routes API,
en utilisant le gestionnaire de sessions unifié pour la gestion des sessions
synchrone et asynchrone.
"""
from __future__ import annotations
from typing import Generator, AsyncGenerator, TYPE_CHECKING, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import verify_token
from app.db import get_db, get_async_db, AsyncSessionLocal

# Import différé pour éviter les imports circulaires
if TYPE_CHECKING:
    from app.db.models.base import User
    from app import crud, models

# Schéma OAuth2 pour l'authentification par token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# Alias pour la rétrocompatibilité
get_db_session = get_db

# Nouvelle fonction pour obtenir une session asynchrone
get_async_db_session = get_async_db

async def get_current_user(
    db: AsyncSession = Depends(get_async_db), 
    token: str = Depends(reusable_oauth2)
) -> 'models.User':
    """
    Obtient l'utilisateur actuellement authentifié.
    
    Args:
        db: Session de base de données asynchrone
        token: JWT token d'authentification
        
    Returns:
        models.User: L'utilisateur authentifié
        
    Raises:
        HTTPException: Si l'authentification échoue
    """
    try:
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
        )
    
    user = await crud.crud_user.get_user_by_username(db, username=username)
    if not user:
        await db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

async def get_current_active_user(
    current_user: 'models.User' = Depends(get_current_user),
) -> 'models.User':
    """
    Vérifie que l'utilisateur actuel est actif.
    
    Args:
        current_user: L'utilisateur actuellement authentifié
        
    Returns:
        models.User: L'utilisateur si actif
        
    Raises:
        HTTPException: Si l'utilisateur est inactif
    """
    if not crud.crud_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: 'models.User' = Depends(get_current_user),
) -> 'models.User':
    """
    Vérifie que l'utilisateur actuel est un superutilisateur.
    
    Args:
        current_user: L'utilisateur actuellement authentifié
        
    Returns:
        models.User: L'utilisateur si superutilisateur
        
    Raises:
        HTTPException: Si l'utilisateur n'a pas les privilèges suffisants
    """
    if not crud.crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    return current_user
