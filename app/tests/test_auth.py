"""
Tests pour les endpoints d'authentification.

Ces tests vérifient le bon fonctionnement des endpoints d'authentification
en utilisant le gestionnaire de sessions unifié.
"""

import logging
import os
from typing import Any, Dict

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from app.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.models.base import User

# Utilisation de la même instance de settings que le reste de l'application
app_settings = settings


async def test_register_user(
    async_client: TestClient, db_session: AsyncSession
) -> None:
    """
    Teste l'enregistrement d'un nouvel utilisateur.

    Vérifie que l'utilisateur peut s'enregistrer avec succès et que les données
    sont correctement enregistrées en base de données.
    """
    logger.info("Début du test d'enregistrement utilisateur")

    # Données du nouvel utilisateur
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }

    logger.debug(f"Données utilisateur pour le test: {user_data}")

    try:
        logger.debug("Appel à l'endpoint d'enregistrement...")
        # Appel à l'endpoint d'enregistrement
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/register",
            json=user_data,
        )
        logger.debug(
            f"Réponse reçue - Statut: {response.status_code}, Contenu: {response.text}"
        )

        # Vérifications de la réponse
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"

        data = response.json()
        assert (
            data["email"] == user_data["email"]
        ), f"Expected email {user_data['email']}, got {data.get('email')}"
        assert (
            data["username"] == user_data["username"]
        ), f"Expected username {user_data['username']}, got {data.get('username')}"
        assert (
            "hashed_password" not in data
        ), "Hashed password should not be in response"
        assert "id" in data, "User ID should be in response"

        # Vérification dans la base de données
        result = await db_session.execute(
            select(User).where(User.email == user_data["email"])
        )
        user = result.scalars().first()

        assert user is not None, "User not found in database"
        assert (
            user.email == user_data["email"]
        ), f"Expected email {user_data['email']} in DB, got {user.email}"
        assert (
            user.username == user_data["username"]
        ), f"Expected username {user_data['username']} in DB, got {user.username}"
        assert user.is_active is True, "New user should be active by default"
        assert (
            user.hashed_password != user_data["password"]
        ), "Password should be hashed"

    except Exception as e:
        await db_session.rollback()
        raise AssertionError(f"Test failed: {str(e)}") from e


async def test_register_existing_email(
    async_client: TestClient, db_session: AsyncSession
) -> None:
    """
    Teste l'enregistrement avec un email déjà existant.

    Vérifie qu'une erreur est renvoyée lors de la tentative de création
    d'un compte avec un email déjà utilisé.
    """
    # Données de l'utilisateur existant
    existing_email = "existing@example.com"
    existing_user = User(
        username="existinguser",
        email=existing_email,
        hashed_password=get_password_hash("testpassword123"),
        full_name="Existing User",
        is_active=True,
    )

    try:
        # Création de l'utilisateur existant
        db_session.add(existing_user)
        await db_session.commit()

        # Tentative d'enregistrement avec le même email
        new_user_data = {
            "username": "newuser",
            "email": existing_email,  # Email déjà utilisé
            "password": "newpassword123",
            "full_name": "New User",
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/register",
            json=new_user_data,
        )

        # Vérifications
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f"Expected status code 400, got {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "detail" in data, "Error detail should be in response"
        assert (
            "already registered" in data["detail"].lower()
        ), f"Expected 'already registered' in error message, got: {data.get('detail', '')}"

        # Vérifier que le nouvel utilisateur n'a pas été créé
        result = await db_session.execute(
            select(User).where(User.username == new_user_data["username"])
        )
        user = result.scalars().first()
        assert user is None, "User with duplicate email should not be created"

    except Exception as e:
        await db_session.rollback()
        raise AssertionError(f"Test failed: {str(e)}") from e


async def test_register_existing_username(
    async_client: TestClient, db_session: AsyncSession
) -> None:
    """
    Teste l'enregistrement avec un nom d'utilisateur déjà existant.

    Vérifie qu'une erreur est renvoyée lors de la tentative de création
    d'un compte avec un nom d'utilisateur déjà utilisé.
    """
    # Données de l'utilisateur existant
    existing_username = "existinguser"
    existing_user = User(
        username=existing_username,
        email="existing@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Existing User",
        is_active=True,
    )

    try:
        # Création de l'utilisateur existant
        db_session.add(existing_user)
        await db_session.commit()

        # Tentative d'enregistrement avec le même nom d'utilisateur
        new_user_data = {
            "username": existing_username,  # Nom d'utilisateur déjà utilisé
            "email": "newemail@example.com",
            "password": "newpassword123",
            "full_name": "New User",
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/register",
            json=new_user_data,
        )

        # Vérifications
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f"Expected status code 400, got {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "detail" in data, "Error detail should be in response"
        assert (
            "already exists" in data["detail"].lower()
        ), f"Expected 'already exists' in error message, got: {data.get('detail', '')}"

        # Vérifier que le nouvel utilisateur n'a pas été créé
        result = await db_session.execute(
            select(User).where(User.email == new_user_data["email"])
        )
        user = result.scalars().first()
        assert user is None, "User with duplicate username should not be created"

    except Exception as e:
        await db_session.rollback()
        raise AssertionError(f"Test failed: {str(e)}") from e


async def test_login_successful(
    async_client: TestClient, db_session: AsyncSession
) -> None:
    """
    Teste la connexion avec des identifiants valides.

    Vérifie qu'un utilisateur peut se connecter avec succès et qu'un token d'accès
    valide est renvoyé.
    """
    # Données de l'utilisateur de test
    test_username = "testuser"
    test_password = "testpassword123"
    test_email = "test@example.com"

    # Création de l'utilisateur de test
    user = User(
        username=test_username,
        email=test_email,
        hashed_password=get_password_hash(test_password),
        full_name="Test User",
        is_active=True,
    )

    try:
        # Ajout de l'utilisateur à la base de données
        db_session.add(user)
        await db_session.commit()

        # Données de connexion
        login_data = {"username": test_username, "password": test_password}

        # Appel à l'endpoint de connexion
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Vérifications
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "access_token" in data, "Access token should be in response"
        assert isinstance(data["access_token"], str), "Access token should be a string"
        assert len(data["access_token"]) > 0, "Access token should not be empty"
        assert (
            data["token_type"].lower() == "bearer"
        ), f"Expected token type 'bearer', got {data.get('token_type', '')}"

        # Vérification supplémentaire du token (optionnel)
        # token_data = verify_token(data["access_token"])
        # assert token_data is not None, "Token should be valid"
        # assert token_data.username == test_username, "Token should be for the correct user"

    except Exception as e:
        await db_session.rollback()
        raise AssertionError(f"Test failed: {str(e)}") from e


async def test_login_invalid_username(async_client: TestClient) -> None:
    """
    Teste la connexion avec un nom d'utilisateur invalide.

    Vérifie qu'une erreur est renvoyée lors de la tentative de connexion
    avec un nom d'utilisateur qui n'existe pas.
    """
    # Données de connexion avec un nom d'utilisateur inexistant
    login_data = {"username": "nonexistent_user_123", "password": "password123"}

    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Vérifications
    assert (
        response.status_code == status.HTTP_401_UNAUTHORIZED
    ), f"Expected status code 401, got {response.status_code}. Response: {response.text}"

    data = response.json()
    assert "detail" in data, "Error detail should be in response"
    assert any(
        msg in data["detail"].lower() for msg in ["incorrect", "invalid", "wrong"]
    ), f"Expected 'incorrect' or similar in error message, got: {data.get('detail', '')}"


async def test_login_invalid_password(
    async_client: TestClient, db_session: AsyncSession
) -> None:
    """
    Teste la connexion avec un mot de passe invalide.

    Vérifie qu'une erreur est renvoyée lors de la tentative de connexion
    avec un mot de passe incorrect.
    """
    # Données de l'utilisateur de test
    test_username = "testuser"
    test_password = "correct_password_123"
    wrong_password = "wrong_password_456"

    # Création de l'utilisateur de test
    user = User(
        username=test_username,
        email="test@example.com",
        hashed_password=get_password_hash(test_password),
        full_name="Test User",
        is_active=True,
    )

    try:
        # Ajout de l'utilisateur à la base de données
        db_session.add(user)
        await db_session.commit()

        # Données de connexion avec un mot de passe incorrect
        login_data = {
            "username": test_username,
            "password": wrong_password,  # Mot de passe incorrect
        }

        # Appel à l'endpoint de connexion
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Vérifications
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), f"Expected status code 401, got {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "detail" in data, "Error detail should be in response"
        assert any(
            msg in data["detail"].lower() for msg in ["incorrect", "invalid", "wrong"]
        ), f"Expected 'incorrect' or similar in error message, got: {data.get('detail', '')}"

    except Exception as e:
        await db_session.rollback()
        raise AssertionError(f"Test failed: {str(e)}") from e


async def test_test_token(
    async_client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    """
    Teste la validation d'un token JWT valide.

    Vérifie que l'endpoint de test de token renvoie les informations
    de l'utilisateur lorsque le token est valide.
    """
    # Appel à l'endpoint de test de token avec des en-têtes d'authentification valides
    response = await async_client.get(
        f"{settings.API_V1_STR}/auth/login/test-token",
        headers=normal_user_token_headers,
    )

    # Vérifications
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Expected status code 200, got {response.status_code}. Response: {response.text}"

    data = response.json()
    assert "email" in data, "Email should be in response"
    assert (
        data["email"] == "test@example.com"
    ), f"Expected email 'test@example.com', got {data.get('email')}"
    assert "id" in data, "User ID should be in response"
    assert "hashed_password" not in data, "Hashed password should not be in response"
    assert "is_active" in data, "is_active flag should be in response"
    assert data["is_active"] is True, "User should be active"
