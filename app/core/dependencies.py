"""
Dépendances FastAPI pour l'application.
"""
from typing import Generator

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
from app import crud


def get_db() -> Generator:
    """
    Fournit une session de base de données.
    
    Yields:
        Session: Une session SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
