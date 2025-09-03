"""
Dépendances FastAPI pour l'application.

ATTENTION: Ce fichier contient encore des fonctions synchrones avec get_db pour rétrocompatibilité.
Pour les nouvelles implémentations, utiliser les fonctions Async depuis app.db directement.
"""
from typing import Generator, Optional

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

# Schéma OAuth2 pour l'authentification par token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

from app.config import settings
from app.core.api.audiobookshelf import AudiobookshelfClient
from app.db.database import SessionLocal
from app.db import get_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud

def get_audiobookshelf_client(instance_id: int = None) -> AudiobookshelfClient:
    """
    Fournit une instance du client Audiobookshelf.

    Args:
        instance_id: ID de l'instance spécifique (optionnel). Si None, utilise la première instance active.

    Returns:
        AudiobookshelfClient: Une instance configurée du client

    Raises:
        HTTPException: Si la configuration est manquante ou instance non trouvée
    """
    from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService

    db = SessionLocal()
    try:
        service = AudiobookshelfInstanceService(db)

        if instance_id:
            instance = service.get_instance(instance_id)
            if not instance or not instance.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Instance Audiobookshelf {instance_id} non trouvée ou inactive"
                )
        else:
            # Utiliser la première instance active comme défaut
            instances = service.get_instances(only_active=True)
            if not instances:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Aucune instance Audiobookshelf active configurée"
                )
            instance = instances[0]

        # Récupérer le token déchiffré
        token = service.get_decrypted_token(instance.id)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Impossible de récupérer le token pour l'instance {instance.name}"
            )

        return AudiobookshelfClient(instance.base_url, token)

    finally:
        db.close()


from functools import partial


def get_audiobookshelf_client_by_instance(instance_id: Optional[int] = None) -> AudiobookshelfClient:
    """
    Fonction factory pour obtenir un client Audiobookshelf avec un ID spécifique.
    À utiliser comme dépendance FastAPI.

    Args:
        instance_id: ID de l'instance (sera injecté par FastAPI depuis les paramètres de requête). Si None, utilise la première instance active.

    Returns:
        AudiobookshelfClient: Client configuré pour l'instance sélectionnée
    """
    return get_audiobookshelf_client(instance_id)


# Créer une dépendance par défaut pour la rétrocompatibilité
get_audiobookshelf_client_default = partial(get_audiobookshelf_client_by_instance, instance_id=None)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
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
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
        
    return user
