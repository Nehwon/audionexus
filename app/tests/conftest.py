"""
Configuration et fixtures partagées pour les tests asynchrones.
"""
import os
import asyncio
import pytest
import pytest_asyncio

# Définir la variable d'environnement TESTING avant d'importer l'application
os.environ["TESTING"] = "1"

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from typing import AsyncGenerator, Dict, Generator

from app.main import app
from app.db.database import Base, get_db
from app.config import settings
from app.core.security import create_access_token
from app.db.models.base import User

# Configuration de la base de données de test
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Moteur de base de données de test
engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Session de test
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Fixture pour la session de base de données
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Crée une nouvelle base de données en mémoire pour chaque test."""
    print("\n=== Début de la fixture db_session ===")
    
    # Afficher les tables avant création
    print("\n=== AVANT CRÉATION DES TABLES ===")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print(f"Tables avant création: {tables}")
    
    # Création des tables
    print("\n=== CRÉATION DES TABLES ===")
    print(f"Métadonnées des tables: {Base.metadata.tables.keys()}")
    
    async with engine.begin() as conn:
        print("Appel à Base.metadata.create_all()...")
        await conn.run_sync(Base.metadata.create_all)
    
    # Afficher les tables après création
    print("\n=== APRÈS CRÉATION DES TABLES ===")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print(f"Tables après création: {tables}")
        
        # Afficher les détails de chaque table
        for table_name in tables:
            print(f"\nStructure de la table {table_name}:")
            try:
                result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = [row[1] for row in result]
                print(f"  Colonnes: {columns}")
            except Exception as e:
                print(f"  Erreur lors de la récupération des colonnes: {e}")
    
    # Création d'une nouvelle session
    print("Création d'une nouvelle session...")
    async with TestingSessionLocal() as session:
        yield session
        print("Rollback de la session...")
        await session.rollback()
    
    # Nettoyage
    print("Nettoyage des tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("=== Fin de la fixture db_session ===\n")

# Fixture pour le client de test asynchrone
@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Crée un client de test asynchrone FastAPI avec une base de données propre."""
    # Surcharge de la dépendance get_db
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Création du client de test asynchrone
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    
    # Nettoyage
    app.dependency_overrides.clear()

# Fixture pour le client de test synchrone (compatibilité)
@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Crée un client de test FastAPI synchrone avec une base de données propre."""
    # Surcharge de la dépendance get_db
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Création du client de test synchrone
    with TestClient(app) as test_client:
        yield test_client
    
    # Nettoyage
    app.dependency_overrides.clear()

# Fixture pour les données de test
@pytest.fixture(scope="function")
async def test_data():
    """Retourne des données de test communes."""
    return {
        "user": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
        },
        "token": {
            "access_token": "test_access_token",
            "token_type": "bearer"
        }
    }

# Fixture pour un utilisateur normal
@pytest_asyncio.fixture(scope="function")
async def normal_user(db_session: AsyncSession) -> User:
    """Crée un utilisateur normal pour les tests."""
    from app.core.security import get_password_hash
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
    return user

# Fixture pour les en-têtes d'authentification d'un utilisateur normal
@pytest.fixture(scope="function")
def normal_user_token_headers(normal_user: User) -> Dict[str, str]:
    """Retourne les en-têtes d'authentification pour un utilisateur normal."""
    access_token = create_access_token(
        data={"sub": normal_user.username}
    )
    return {"Authorization": f"Bearer {access_token}"}
