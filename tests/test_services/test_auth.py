"""Tests pour les services d'authentification."""
import pytest
from datetime import timedelta
from unittest.mock import patch

from app.services import auth
from app.db.models import User
from app.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotActiveError,
    InvalidTokenError,
    InvalidCredentialsError
)


def test_create_verify_token(app):
    """Teste la création et la vérification d'un token JWT."""
    with app.app_context():
        # Créer un token
        token = auth.create_access_token(1, app=app)
        assert isinstance(token, str)
        
        # Vérifier le token
        decoded = auth.verify_access_token(token, app=app)
        assert decoded["sub"] == "1"


def test_authenticate_user_success(db_session):
    """Teste l'authentification réussie."""
    # Créer un utilisateur avec un mot de passe hashé
    user = User(
        username="testuser",
        email="test@example.com"
    )
    user.set_password("testpassword")
    
    db_session.add(user)
    db_session.commit()
    
    # Tester l'authentification
    auth_user = auth.authenticate_user("test@example.com", "testpassword")
    assert auth_user is not None
    assert auth_user.email == "test@example.com"


def test_register_user_duplicate_email(db_session):
    """Teste l'échec de l'enregistrement avec un email existant."""
    # Créer un utilisateur existant
    existing_user = User(
        username="existing",
        email="existing@example.com"
    )
    existing_user.set_password("test123")
    db_session.add(existing_user)
    db_session.commit()
    
    # Tester l'enregistrement avec le même email
    with pytest.raises(UserAlreadyExistsError):
        auth.register_user(
            {"username": "newuser", "email": "existing@example.com", "password": "test123"},
            db_session
        )


def test_generate_verify_password_reset_token(app):
    """Teste la génération et la vérification d'un token de réinitialisation."""
    with app.app_context():
        # Générer un token
        email = "test@example.com"
        token = auth.generate_password_reset_token(email)
        
        # Vérifier le token
        assert auth.verify_password_reset_token(token) == email
