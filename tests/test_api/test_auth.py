"""
Tests pour les endpoints d'authentification de l'API.
"""
import pytest
from flask import json


def test_register_user(client, db_session):
    """Teste l'enregistrement d'un nouvel utilisateur."""
    # Données de test
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
        "confirm_password": "securepassword123"
    }
    
    # Act
    response = client.post(
        "/api/auth/register",
        data=json.dumps(user_data),
        content_type="application/json"
    )
    
    # Assert
    assert response.status_code == 201
    assert response.is_json
    assert "id" in response.json
    assert "username" in response.json
    assert response.json["username"] == user_data["username"]
    assert "email" in response.json
    assert response.json["email"] == user_data["email"]
    assert "password" not in response.json  # Le mot de passe ne doit pas être renvoyé


def test_login_user(client, test_user):
    """Teste la connexion d'un utilisateur."""
    # Données de test
    login_data = {
        "email": test_user.email,
        "password": "testpassword"
    }
    
    # Act
    response = client.post(
        "/api/auth/login",
        data=json.dumps(login_data),
        content_type="application/json"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.is_json
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert "user" in response.json
    assert response.json["user"]["email"] == test_user.email


def test_protected_route_without_token(client):
    """Teste l'accès à une route protégée sans token."""
    # Act
    response = client.get("/api/protected")
    
    # Assert
    assert response.status_code == 401
    assert response.is_json
    assert "message" in response.json
    assert "Missing Authorization Header" in response.json["message"]


def test_protected_route_with_valid_token(client, test_user, test_token):
    """Teste l'accès à une route protégée avec un token valide."""
    # Act
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.is_json
    assert "message" in response.json
    assert "protected" in response.json["message"].lower()


class TestPasswordReset:
    """Tests pour la réinitialisation du mot de passe."""
    
    def test_request_password_reset(self, client, test_user, mocker):
        """Teste la demande de réinitialisation de mot de passe."""
        # Mock de l'envoi d'email
        mock_send = mocker.patch('app.services.email.send_password_reset_email')
        
        # Données de test
        data = {"email": test_user.email}
        
        # Act
        response = client.post(
            "/api/auth/forgot-password",
            data=json.dumps(data),
            content_type="application/json"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.is_json
        assert "message" in response.json
        assert "email sent" in response.json["message"].lower()
        mock_send.assert_called_once()
    
    def test_reset_password_with_valid_token(self, client, test_user):
        """Teste la réinitialisation du mot de passe avec un token valide."""
        # Générer un token de réinitialisation
        from app.services.auth import generate_password_reset_token
        token = generate_password_reset_token(test_user.email)
        
        # Données de test
        data = {
            "token": token,
            "new_password": "newsecurepassword123",
            "confirm_password": "newsecurepassword123"
        }
        
        # Act
        response = client.post(
            "/api/auth/reset-password",
            data=json.dumps(data),
            content_type="application/json"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.is_json
        assert "message" in response.json
        assert "password updated" in response.json["message"].lower()
    
    def test_reset_password_with_invalid_token(self, client, test_user):
        """Teste la réinitialisation du mot de passe avec un token invalide."""
        # Données de test avec token invalide
        data = {
            "token": "invalid.token.here",
            "new_password": "newsecurepassword123",
            "confirm_password": "newsecurepassword123"
        }
        
        # Act
        response = client.post(
            "/api/auth/reset-password",
            data=json.dumps(data),
            content_type="application/json"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.is_json
        assert "error" in response.json
        assert "invalid" in response.json["error"].lower()
