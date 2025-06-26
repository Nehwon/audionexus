"""
Configuration et fixtures partagées pour les tests asynchrones.
"""
import os
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Generator, Any

# Désactiver les logs SQLAlchemy pendant les tests
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Charger la configuration de test avant tout autre import
from .test_config import test_settings, apply_test_settings

# Appliquer la configuration de test avant tout import d'application
apply_test_settings()

# Maintenant que la configuration est appliquée, nous pouvons importer les modules de l'application
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from app.main import app
from app.db.database import Base, init_db, SessionLocal as DBSessionLocal
from app.core.security import create_access_token, get_password_hash
from app.db.models.base import User
from app.db import get_db as get_db_dep, get_async_db, async_engine, AsyncSessionLocal
from app.core.deps import oauth2_scheme

# Configuration de la base de données de test
TEST_SQLALCHEMY_DATABASE_URL = test_settings.DATABASE_URI

# Création d'un moteur SQLite en mémoire pour les tests
@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Crée un moteur SQLite en mémoire pour les tests."""
    from sqlalchemy.ext.asyncio import create_async_engine
    
    engine = create_async_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_SQLALCHEMY_DATABASE_URL else {}
    )
    
    # Création des tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Nettoyage
    await engine.dispose()

# Nettoyage de la base de données avant chaque test
async def cleanup_database(async_engine: AsyncEngine):
    """Nettoie toutes les tables de la base de données avant chaque test."""
    async with async_engine.begin() as conn:
        # Désactiver temporairement les contraintes de clé étrangère pour SQLite
        if 'sqlite' in str(async_engine.url):
            await conn.execute(text('PRAGMA foreign_keys = OFF'))
        
        # Supprimer toutes les données des tables
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
        
        # Réactiver les contraintes de clé étrangère pour SQLite
        if 'sqlite' in str(async_engine.url):
            await conn.execute(text('PRAGMA foreign_keys = ON'))

# Configuration de la session de test asynchrone
@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Crée une nouvelle session de base de données pour chaque test.
    
    - Nettoie la base de données avant chaque test
    - Utilise une transaction qui est annulée à la fin du test
    - Ne laisse pas de données résiduelles dans la base de données
    - Gère correctement les erreurs et le nettoyage
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # Nettoyer la base de données avant chaque test
    await cleanup_database(async_engine)
    
    # Créer une nouvelle session avec un rollback automatique en cas d'erreur
    connection = await async_engine.connect()
    transaction = await connection.begin()
    
    # Créer une session liée à cette transaction
    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    # S'assurer que la session utilise notre transaction
    session.sync_session.begin_nested()
    
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

# Surcharge de la dépendance get_db pour les tests
@pytest_asyncio.fixture(autouse=True)
async def override_dependencies(db_session: AsyncSession):
    """Surcharge les dépendances de l'application pour les tests."""
    
    async def override_get_db():
        """Remplace la dépendance get_db pour utiliser la session de test."""
        try:
            yield db_session
        finally:
            await db_session.close()
    
    # Surcharger les dépendances
    app.dependency_overrides[get_db_dep] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_db
    
    yield
    
    # Nettoyer les surcharges
    app.dependency_overrides.clear()


# Fixture pour le client de test asynchrone
@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Crée un client de test asynchrone FastAPI avec une base de données propre.
    
    - Utilise ASGITransport pour une intégration complète avec FastAPI
    - Nettoie les dépendances après utilisation
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        try:
            yield client
        finally:
            # Nettoyage des dépendances
            app.dependency_overrides.clear()

# Fixture pour le client de test synchrone (compatibilité)
@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Crée un client de test FastAPI synchrone avec une base de données propre."""
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
