"""
Tests pour les endpoints d'authentification.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.db.models.base import UserCreate, User
from app.core.security import get_password_hash

async def test_register_user(async_client: TestClient, db_session: AsyncSession) -> None:
    """Teste l'enregistrement d'un nouvel utilisateur."""
    # Données du nouvel utilisateur
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    # Appel à l'endpoint d'enregistrement
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data,
    )
    
    # Vérifications
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "id" in data
    
    # Vérification dans la base de données
    result = await db_session.execute(select(User).where(User.email == user_data["email"]))
    user = result.scalars().first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]

async def test_register_existing_email(async_client: TestClient, db_session: AsyncSession) -> None:
    """Teste l'enregistrement avec un email déjà existant."""
    # Création d'un utilisateur existant
    user = User(
        username="existinguser",
        email="existing@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Existing User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Tentative d'enregistrement avec le même email
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "username": "newuser",
            "email": "existing@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        },
    )
    
    # Vérifications
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "email already registered" in data["detail"]
    assert data["username"] == "newuser"
    assert "hashed_password" not in data
    assert "id" in data

async def test_register_existing_username(async_client: TestClient, db_session: AsyncSession) -> None:
    """Teste l'enregistrement avec un nom d'utilisateur déjà existant."""
    # Création d'un utilisateur existant
    user = User(
        username="existinguser",
        email="existing@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Existing User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Tentative d'enregistrement avec le même nom d'utilisateur
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "username": "existinguser",
            "email": "newemail@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        },
    )
    
    # Vérifications
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "username already exists" in data["detail"].lower()

async def test_login_successful(async_client: TestClient, db_session: AsyncSession) -> None:
    """Teste la connexion avec des identifiants valides."""
    # Création d'un utilisateur de test
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Données de connexion
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    # Appel à l'endpoint de connexion
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Vérifications
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_username(async_client: TestClient) -> None:
    """Teste la connexion avec un nom d'utilisateur invalide."""
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={"username": "nonexistent", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "incorrect username or password" in data["detail"].lower()

async def test_login_invalid_password(async_client: TestClient, db_session: AsyncSession) -> None:
    """Teste la connexion avec un mot de passe invalide."""
    # Création d'un utilisateur de test
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Données de connexion avec un mot de passe invalide
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    # Appel à l'endpoint de connexion
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Vérifications
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "Incorrect username or password" in data["detail"].lower()

def test_test_token(client: TestClient, normal_user_token_headers: dict) -> None:
    # Appel à l'endpoint de test de token avec des en-têtes d'authentification valides
    response = client.get(
        f"{settings.API_V1_STR}/auth/login/test-token",
        headers=normal_user_token_headers
    )
    
    # Vérifications
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data
