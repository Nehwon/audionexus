"""
Services d'authentification pour l'application AudioNexus.

Ce module fournit des fonctions pour gérer l'authentification des utilisateurs,
la création et la vérification des tokens JWT, et la gestion des mots de passe.
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from flask import current_app

from flask_sqlalchemy import SQLAlchemy
from app.db import SessionLocal
from app.db.models import User
from app.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotActiveError,
    InvalidTokenError,
    InvalidCredentialsError
)


def create_access_token(user_id: int, app=None) -> str:
    """
    Crée un token JWT d'accès.
    
    Args:
        user_id: ID de l'utilisateur
        app: Instance de l'application Flask (optionnel)
        
    Returns:
        str: Token JWT encodé
    """
    from flask import current_app
    
    app = app or current_app._get_current_object()
    
    with app.app_context():
        expires = datetime.utcnow() + timedelta(
            minutes=app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 60)
        )
        token_data = {
            'sub': str(user_id),
            'exp': expires,
            'type': 'access'
        }
        return jwt.encode(
            token_data,
            app.config['JWT_SECRET_KEY'],
            algorithm=app.config.get('JWT_ALGORITHM', 'HS256')
        )


def decode_token(token: str, app=None) -> dict:
    """
    Décode et valide un token JWT.
    
    Args:
        token: Token JWT à décoder
        app: Instance de l'application Flask (optionnel)
        
    Returns:
        dict: Données décodées du token
        
    Raises:
        JWTError: Si le token est invalide ou expiré
    """
    from flask import current_app
    
    app = app or current_app._get_current_object()
    
    with app.app_context():
        try:
            return jwt.decode(
                token,
                app.config['JWT_SECRET_KEY'],
                algorithms=[app.config.get('JWT_ALGORITHM', 'HS256')]
            )
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError('Token expiré')
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f'Token invalide: {str(e)}')


def authenticate_user(email: str, password: str) -> User:
    """
    Authentifie un utilisateur avec son email et son mot de passe.

    Args:
        email: L'email de l'utilisateur
        password: Le mot de passe en clair

    Returns:
        User: L'utilisateur authentifié

    Raises:
        InvalidCredentialsError: Si les identifiants sont incorrects
        UserNotActiveError: Si le compte utilisateur est désactivé
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
    finally:
        db.close()
    if not user or not user.check_password(password):
        raise InvalidCredentialsError("Email ou mot de passe incorrect")
    
    if not user.is_active:
        raise UserNotActiveError("Ce compte est désactivé")
    
    return user


def register_user(email: str, password: str, **kwargs) -> User:
    """
    Enregistre un nouvel utilisateur.

    Args:
        email: L'email de l'utilisateur
        password: Le mot de passe en clair
        **kwargs: Autres attributs optionnels de l'utilisateur

    Returns:
        User: L'utilisateur créé

    Raises:
        UserAlreadyExistsError: Si un utilisateur avec cet email existe déjà
    """
    db = SessionLocal()
    try:
        # Vérifier si l'utilisateur existe déjà
        if db.query(User).filter(User.email == email).first():
            raise UserAlreadyExistsError("Un utilisateur avec cet email existe déjà")
        
        # Créer le nouvel utilisateur
        user = User(email=email, **kwargs)
        user.set_password(password)
        
        # Ajouter et sauvegarder l'utilisateur
        db.add(user)
        db.commit()
        
        return user
    finally:
        db.close()


def create_refresh_token(user_id: int, app=None) -> str:
    """
    Crée un token JWT de rafraîchissement.
    
    Args:
        user_id: ID de l'utilisateur
        app: Instance de l'application Flask (optionnel)
        
    Returns:
        str: Token JWT encodé
    """
    from flask import current_app
    
    app = app or current_app._get_current_object()
    
    with app.app_context():
        expires = datetime.utcnow() + timedelta(
            days=app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 30)
        )
        token_data = {
            'sub': str(user_id),
            'exp': expires,
            'type': 'refresh'
        }
        return jwt.encode(
            token_data,
            app.config['JWT_SECRET_KEY'],
            algorithm=app.config.get('JWT_ALGORITHM', 'HS256')
        )


def generate_password_reset_token(email: str) -> str:
    """
    Génère un token pour la réinitialisation du mot de passe.

    Args:
        email: L'email de l'utilisateur

    Returns:
        str: Le token de réinitialisation
    """
    expires = datetime.utcnow() + timedelta(hours=1)
    to_encode = {
        "exp": expires,
        "sub": email,
        "type": "reset"
    }
    return jwt.encode(
        to_encode,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config.get('JWT_ALGORITHM', 'HS256')
    )


def verify_password_reset_token(token: str) -> str:
    """
    Vérifie un token de réinitialisation de mot de passe.
    
    Args:
        token: Le token à vérifier

    Returns:
        str: L'email de l'utilisateur si le token est valide

    Raises:
        InvalidTokenError: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
        )
        if payload.get('type') != 'reset':
            raise InvalidTokenError("Type de token invalide")
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Le token de réinitialisation a expiré")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Token de réinitialisation invalide")
