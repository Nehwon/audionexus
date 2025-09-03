"""
Configuration pour les tests d'intégration de VoidAuth.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

# Mock pour le client VoidAuth
class MockVoidAuthClient:
    """Mock pour le client VoidAuth à utiliser dans les tests."""
    
    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.next_id = 1
    
    async def create_user(self, username, email, password, **kwargs):
        """Crée un utilisateur de test."""
        user_id = f"user-{self.next_id}"
        self.next_id += 1
        
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "enabled": True,
            "emailVerified": False,
            **kwargs
        }
        
        self.users[user_id] = {
            "user": user,
            "password": password
        }
        
        return user
    
    async def authenticate_user(self, username, password):
        """Authentifie un utilisateur de test."""
        for user_id, data in self.users.items():
            if (data["user"]["username"] == username or 
                data["user"]["email"] == username) and \
               data["password"] == password:
                
                # Générer un faux token
                token = f"fake-jwt-token-{user_id}"
                self.tokens[token] = user_id
                
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "refresh_token": f"fake-refresh-token-{user_id}"
                }
        return None
    
    async def get_user_info(self, token):
        """Récupère les informations d'un utilisateur à partir d'un token."""
        user_id = self.tokens.get(token.split()[-1] if ' ' in token else token)
        if user_id and user_id in self.users:
            return self.users[user_id]["user"]
        return None

# Fixture pour le client de test
@pytest.fixture(scope="module")
def test_client():
    """Crée un client de test FastAPI."""
    with TestClient(app) as client:
        yield client

# Fixture pour le mock VoidAuth
@pytest.fixture(scope="module")
def mock_voidauth():
    """Crée un mock pour le service VoidAuth."""
    mock_client = MockVoidAuthClient()
    
    # Créer un utilisateur de test
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    # Ajouter l'utilisateur au mock
    user = mock_client.create_user(
        username=test_user["username"],
        email=test_user["email"],
        password=test_user["password"],
        firstName=test_user["full_name"].split(" ")[0],
        lastName=" ".join(test_user["full_name"].split(" ")[1:]) if " " in test_user["full_name"] else "",
        enabled=True,
        emailVerified=False
    )
    
    return mock_client, test_user

# Patch pour le service VoidAuth
@pytest.fixture(scope="module")
def voidauth_service_mock(mock_voidauth):
    """Patch le service VoidAuth pour utiliser le mock."""
    mock_client, _ = mock_voidauth
    
    with patch('app.services.voidauth_service.voidauth_service', mock_client):
        yield mock_client
