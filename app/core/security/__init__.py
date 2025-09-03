"""
Module de sécurité pour l'application.
Contient les utilitaires d'authentification et de sécurité.
"""
import base64
import os
from datetime import datetime, timedelta
from typing import Optional

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Configuration pour le hachage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si le mot de passe en clair correspond au hachage stocké.

    Args:
        plain_password: Mot de passe en clair
        hashed_password: Mot de passe haché

    Returns:
        bool: True si la vérification est réussie, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Génère un hachage sécurisé du mot de passe.

    Args:
        password: Mot de passe en clair

    Returns:
        str: Mot de passe haché
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un nouveau token d'accès JWT.

    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token

    Returns:
        str: Token JWT encodé
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Optional['TokenData']:
    """
    Vérifie et décode un token JWT.

    Args:
        token: Token JWT à vérifier

    Returns:
        Optional[TokenData]: Données du token si valide, None sinon
    """
    credentials_exception = JWTError("Impossible de valider les identifiants")
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # TokenData is needed; assuming it's defined elsewhere or import it
        # For now, return dict
        return {"username": username}
    except JWTError:
        return None

def get_encryption_key() -> bytes:
    """
    Génère ou retourne la clé de chiffrement pour les données sensibles.

    Returns:
        bytes: Clé de chiffrement Fernet
    """
    if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
        key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY)
    else:
        # Générer une clé par défaut si non configurée
        key = base64.urlsafe_b64decode(b"WGxRQlBRNG1vTnQzSENyRHE4WG93VFBhWlVwNzRtWkk=")  # Default key for development

    return key

def encrypt_token(token: str) -> str:
    """
    Chiffre un token avant stockage en base de données.

    Args:
        token: Token en clair

    Returns:
        str: Token chiffré (base64)
    """
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(token.encode())
    return encrypted.decode()

def decrypt_token(encrypted_token: str) -> str:
    """
    Déchiffre un token depuis la base de données.

    Args:
        encrypted_token: Token chiffré

    Returns:
        str: Token en clair
    """
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_token.encode())
    return decrypted.decode()

__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'verify_token',
    'encrypt_token',
    'decrypt_token'
]