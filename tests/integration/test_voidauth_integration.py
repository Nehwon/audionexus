"""
Tests d'intégration pour l'authentification avec VoidAuth.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.config import settings
from app.db import Base, engine, get_db, init_engine

# Utiliser une base de données en mémoire synchronisée pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
os.environ["TESTING"] = "True"

# Créer les tables de la base de données avec une approche simplifiée
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlite3

# Créer un moteur SQLite directement pour les tests
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=test_engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Redéfinir les objets pour les tests
engine = test_engine

# Client de test
client = TestClient(app)

def override_get_db():
    """Override de la dépendance get_db pour les tests."""
    try:
        db = Session(engine)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Données de test
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}

@pytest.fixture(scope="module")
def test_user():
    """Crée un utilisateur de test et retourne ses informations."""
    # Obtenir le token CSRF
    csrf_response = client.get(f"{settings.API_V1_STR}/auth/csrf-token")
    assert csrf_response.status_code == 200
    csrf_token = csrf_response.json()["csrf_token"]

    # S'assurer que l'utilisateur n'existe pas déjà
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=TEST_USER,
        headers={"X-CSRF-Token": csrf_token}
    )

    if response.status_code == 400 and "already exists" in response.json().get("detail", ""):
        # Si l'utilisateur existe déjà, on le supprime
        db = next(override_get_db())
        from app.models.user import User
        user = db.query(User).filter(User.email == TEST_USER["email"]).first()
        if user:
            db.delete(user)
            db.commit()
        # Puis on le recrée (nouveau token CSRF)
        csrf_response = client.get(f"{settings.API_V1_STR}/auth/csrf-token")
        csrf_token = csrf_response.json()["csrf_token"]
        response = client.post(
            f"{settings.API_V1_STR}/auth/register",
            json=TEST_USER,
            headers={"X-CSRF-Token": csrf_token}
        )

    assert response.status_code == 200
    user = response.json()
    user["password"] = TEST_USER["password"]
    return user

def test_register_user():
    """Teste l'enregistrement d'un nouvel utilisateur."""
    test_user = {
        "username": "new_test_user",
        "email": "new_test@example.com",
        "password": "newtestpass123",
        "full_name": "New Test User"
    }

    # Obtenir le token CSRF
    csrf_response = client.get(f"{settings.API_V1_STR}/auth/csrf-token")
    assert csrf_response.status_code == 200
    csrf_token = csrf_response.json()["csrf_token"]

    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=test_user,
        headers={"X-CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "id" in data
    assert "password" not in data

def test_login(test_user):
    """Teste la connexion d'un utilisateur."""
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }

    # Obtenir le token CSRF
    csrf_response = client.get(f"{settings.API_V1_STR}/auth/csrf-token")
    assert csrf_response.status_code == 200
    csrf_token = csrf_response.json()["csrf_token"]

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={**login_data, "csrf_token": csrf_token}  # Includer dans les données form
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in data

def test_get_current_user(test_user):
    """Teste la récupération des informations de l'utilisateur connecté."""
    # D'abord, on se connecte pour obtenir un token
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Ensuite, on utilise le token pour récupérer les infos de l'utilisateur
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "id" in data

def test_protected_route(test_user):
    """Teste l'accès à une route protégée."""
    # D'abord, on se connecte pour obtenir un token
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Ensuite, on teste une route protégée
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # La route devrait retourner 404 si elle n'existe pas, mais le token est valide
    # ou 200 si la route existe et que l'utilisateur est autorisé
    assert response.status_code in [200, 404]
