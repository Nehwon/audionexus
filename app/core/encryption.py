"""
Module de chiffrement AES-256 pour les données sensibles.
Utilise le module cryptography pour le chiffrement et déchiffrement.
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from app.config import settings

# Clé maître dérivée du secret_key de l'application
def _get_encryption_key() -> bytes:
    """
    Génère une clé de chiffrement AES-256 dérivée du secret de l'application.

    Returns:
        bytes: Clé de chiffrement AES-256
    """
    password = settings.secret_key.encode()
    salt = b'AudioNexus_salt_2024'  # Sel fixe pour la cohérence

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits pour AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    return base64.urlsafe_b64encode(kdf.derive(password))

# Instance Fernet pour le chiffrement
_fernet = Fernet(_get_encryption_key())

def encrypt_data(plain_data: str) -> str:
    """
    Chiffre les données sensibles en AES-256.

    Args:
        plain_data: Données à chiffrer en clair

    Returns:
        str: Données chiffrées en base64
    """
    if not plain_data:
        return ""

    encrypted = _fernet.encrypt(plain_data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data: str) -> str:
    """
    Déchiffre les données sensibles chiffrées en AES-256.

    Args:
        encrypted_data: Données chiffrées en base64

    Returns:
        str: Données déchiffrées

    Raises:
        Exception: Si le déchiffrement échoue
    """
    if not encrypted_data:
        return ""

    try:
        decrypted = _fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        raise Exception(f"Impossible de déchiffrer les données: {str(e)}")

def encrypt_session_data(session_data: dict) -> dict:
    """
    Chiffre les données de session sensibles.

    Args:
        session_data: Dictionnaire de données de session

    Returns:
        dict: Données chiffrées
    """
    sensitive_fields = ['password', 'token', 'secret', 'key', 'credentials']

    encrypted_data = {}
    for key, value in session_data.items():
        if any(field in key.lower() for field in sensitive_fields) and isinstance(value, str):
            encrypted_data[key] = encrypt_data(value)
        else:
            encrypted_data[key] = value

    return encrypted_data

def decrypt_session_data(session_data: dict) -> dict:
    """
    Déchiffre les données de session chiffrées.

    Args:
        session_data: Dictionnaire de données chiffrées

    Returns:
        dict: Données déchiffrées
    """
    decrypted_data = {}
    for key, value in session_data.items():
        if isinstance(value, str) and value.startswith('gAAAAA'):  # Format Fernet
            try:
                decrypted_data[key] = decrypt_data(value)
            except:
                # Si ce n'est pas chiffré ou le déchiffrement échoue, garder tel quel
                decrypted_data[key] = value
        else:
            decrypted_data[key] = value

    return decrypted_data