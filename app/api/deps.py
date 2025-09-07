"""
Dépendances communes pour les routes API.

Ce module fournit des dépendances réutilisables pour les routes API,
en utilisant le gestionnaire de sessions unifié pour la gestion des sessions
synchrone et asynchrone.

NOTE: Toutes les fonctions utilisent maintenant exclusivement get_async_db depuis app.db
pour éviter les dépendances circulaires. Les anciens alias de compatibilité ont été supprimés.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.security as security
from app.config import settings
from app.db import get_async_db

# Import différé pour éviter les imports circulaires
if TYPE_CHECKING:
    from app import crud, models
    from app.db.models.base import User

# Configuration du logger
logger = logging.getLogger(__name__)

# Schéma OAuth2 pour l'authentification par token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


# Définition de get_async_db_session comme une vraie fonction génératrice asynchrone
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fournit une session de base de données asynchrone pour FastAPI.

    À utiliser dans les endpoints FastAPI avec `Depends(get_async_db_session)`.
    """
    async for session in get_async_db():
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_async_db), token: str = Depends(reusable_oauth2)
) -> "models.User":
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
        payload = security.verify_token(token)
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
        logger.error(f"Erreur de validation du token dans get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
        )

    if not username:
        logger.warning("Nom d'utilisateur manquant dans le token")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials: No username in token",
        )

    logger.info(f"Récupération de l'utilisateur {username} depuis la DB")
    user = await crud.crud_user.get_user_by_username(db, username=username)
    if not user:
        logger.warning(f"Utilisateur {username} non trouvé")
        await db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    logger.info(f"Utilisateur {username} authentifié avec succès")
    return user


async def get_current_active_user(
    current_user: "models.User" = Depends(get_current_user),
) -> "models.User":
    """
    Vérifie que l'utilisateur actuel est actif.

    Args:
        current_user: L'utilisateur actuellement authentifié

    Returns:
        models.User: L'utilisateur si actif

    Raises:
        HTTPException: Si l'utilisateur est inactif
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_active_superuser(
    current_user: "models.User" = Depends(get_current_active_user),
) -> "models.User":
    """
    Vérifie que l'utilisateur actuel est un superutilisateur actif.

    Args:
        current_user: L'utilisateur actuellement authentifié et actif

    Returns:
        models.User: L'utilisateur si superutilisateur

    Raises:
        HTTPException: Si l'utilisateur n'est pas un superutilisateur
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
