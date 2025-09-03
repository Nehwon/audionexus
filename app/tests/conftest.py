"""
Configuration et fixtures partagées pour les tests asynchrones.
"""
import os
import asyncio
import logging
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Generator, Any
from fastapi import FastAPI

# Fixture pour l'application FastAPI
@pytest.fixture(scope="module")
def app():
    """Retourne une instance de l'application FastAPI pour les tests."""
    # Désactiver le chargement des variables d'environnement pour les tests
    os.environ["TESTING"] = "true"
    from app.main import app as fastapi_app
    return fastapi_app

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
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from app.main import app
from app.db.database import Base, init_db, SessionLocal as DBSessionLocal
from app.services.auth import create_access_token
import app.core.security as core_security
from app.db.models.base import User
from app.db import get_db as get_db_dep, get_async_db, AsyncSessionLocal
from app.core import deps as core_deps
from app.api import deps as api_deps
from app.core.deps import oauth2_scheme

# Configuration de la base de données de test
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Création d'un moteur SQLite en mémoire pour les tests
@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Crée un moteur SQLite en mémoire pour les tests."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession as AsyncDBSession
    from app.db.session_manager import init_async_engine, AsyncSessionLocal as GlobalAsyncSessionLocal
    
    # Configurer le logger pour le débogage
    logger = logging.getLogger(__name__)
    logger.info("Initialisation du moteur de test asynchrone...")
    
    # Créer le moteur directement pour les tests
    engine = create_async_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        echo=True,  # Activer l'écho pour le débogage
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    # Création des tables
    logger.info("Création des tables de test...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Créer une nouvelle session factory pour les tests
    TestAsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncDBSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )
    
    # S'assurer que le moteur est correctement initialisé dans le gestionnaire de session
    logger.info("Mise à jour du gestionnaire de session global...")
    import app.db.session_manager as session_manager
    
    # Mettre à jour le moteur et la session factory dans le module session_manager
    session_manager.async_engine = engine
    session_manager.AsyncSessionLocal = TestAsyncSessionLocal
    
    logger.info("Moteur de test asynchrone initialisé avec succès")
    
    yield engine
    
    # Nettoyage
    logger.info("Nettoyage du moteur de test asynchrone...")
    await engine.dispose()
    
    # Réinitialiser le moteur global
    session_manager.async_engine = None
    session_manager.AsyncSessionLocal = None
    logger.info("Moteur de test asynchrone nettoyé")

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
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text, inspect
    
    # Créer une factory pour les sessions asynchrones
    async_session_factory = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    # Créer une nouvelle session avec une transaction explicite
    session = async_session_factory()
    
    # Activer les contraintes de clé étrangère pour SQLite
    if 'sqlite' in str(async_engine.url):
        await session.execute(text('PRAGMA foreign_keys=ON'))
    
    # Démarrer une transaction de test
    await session.begin_nested()
    
    try:
        # Nettoyer la base de données avant le test
        await cleanup_database(async_engine)
        
        # Donner la session au test
        yield session
        
        # S'assurer que toutes les opérations sont terminées
        await session.flush()
        
        # Annuler les changements à la fin du test
        await session.rollback()
        
    except Exception as e:
        # En cas d'erreur, annuler les changements
        if session.in_transaction():
            await session.rollback()
        raise e
        
    finally:
        # Nettoyer la session
        if session.in_transaction():
            await session.rollback()
        await session.close()
        
        # Réinitialiser la base de données pour le prochain test
        async with async_engine.begin() as conn:
            if 'sqlite' in str(async_engine.url):
                await conn.execute(text('PRAGMA foreign_keys = OFF'))
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            if 'sqlite' in str(async_engine.url):
                await conn.execute(text('PRAGMA foreign_keys = ON'))

# Surcharge des dépendances pour les tests
@pytest_asyncio.fixture(autouse=True)
async def override_dependencies(db_session: AsyncSession, app: FastAPI):
    """
    Surcharge les dépendances de l'application pour les tests.
    
    Cette fixture s'assure que toutes les variantes des dépendances de base de données
    sont correctement surchargées pour utiliser la session de test.
    """
    # Configuration du logger
    logger = logging.getLogger(__name__)
    logger.info("Configuration des surcharges de dépendances pour les tests...")
    
    # Importer la dépendance canonique
    from app.db import get_async_db
    
    # Fonction de surcharge pour les dépendances asynchrones
    async def override_async_db():
        """Remplace la dépendance asynchrone de base de données pour les tests."""
        logger.debug("Utilisation de la session de test asynchrone dans override_async_db")
        try:
            # S'assurer que la session est valide
            if db_session.in_transaction():
                await db_session.rollback()
                
            # Démarrer une nouvelle transaction imbriquée
            await db_session.begin_nested()
            
            # Fournir la session au test
            yield db_session
            
            # S'assurer que toutes les opérations sont terminées
            await db_session.flush()
            
            # Ne pas faire de commit, la transaction sera annulée par la fixture db_session
            
        except Exception as e:
            logger.error(f"Erreur dans override_async_db: {str(e)}", exc_info=True)
            if db_session.in_transaction():
                await db_session.rollback()
            raise e
    
    # Fonction de surcharge pour get_async_db_session
    async def override_async_db_session():
        """Remplace la dépendance asynchrone get_async_db_session pour les tests."""
        logger.debug("Utilisation de la session de test asynchrone dans override_async_db_session")
        try:
            # S'assurer que la session est valide
            if db_session.in_transaction():
                await db_session.rollback()
            yield db_session
        except Exception as e:
            logger.error(f"Erreur dans override_async_db_session: {str(e)}", exc_info=True)
            if db_session.in_transaction():
                await db_session.rollback()
            raise e

    # S'assurer que le moteur asynchrone est initialisé
    from app.db.session_manager import init_async_engine, async_engine as db_async_engine
    from app.config import settings
    
    # Utiliser l'URL de test pour l'initialisation
    test_db_url = TEST_SQLALCHEMY_DATABASE_URL
    
    if db_async_engine is None:
        logger.info(f"Initialisation du moteur asynchrone pour les tests avec l'URL: {test_db_url}")
        init_async_engine(test_db_url, force=True)
    
    if db_async_engine is None:
        error_msg = "Le moteur asynchrone n'a pas pu être initialisé pour les tests"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    logger.info("Moteur asynchrone initialisé avec succès pour les tests")
    
    # Importer les dépendances à surcharger
    from app.core import deps as core_deps
    from app.api import deps as api_deps
    
    # S'assurer que l'application FastAPI est correctement configurée
    if not hasattr(app, 'dependency_overrides'):
        app.dependency_overrides = {}
    
    # Importer la fonction de dépendance utilisée dans la route /auth/register
    from app.core.deps import get_async_db_session as original_get_async_db_session
    
    logger.info(f"Fonction de dépendance originale (importée depuis app.core.deps): {id(original_get_async_db_session)}")
    logger.info(f"Fonction de remplacement (créée dans conftest): {id(override_async_db_session)}")
    
    # Surcharger les dépendances de base de données
    app.dependency_overrides.update({
        # Surcharge des dépendances asynchrones
        'get_async_db': override_async_db,
        'get_async_db_session': override_async_db_session,
        
        # Surcharge des dépendances synchrones
        'get_db': lambda: db_session.sync_session,
        'get_db_session': lambda: db_session.sync_session,
        
        # Surcharge du schéma OAuth2 pour les tests
        'oauth2_scheme': lambda: "test_token"
    })
    
    # Vérifier que la surcharge a bien été appliquée
    overridden_func = app.dependency_overrides.get('get_async_db_session')
    if overridden_func:
        logger.info(f"Fonction de dépendance surchargée dans app.dependency_overrides: {id(overridden_func)}")
    else:
        logger.warning("La fonction 'get_async_db_session' n'a pas été trouvée dans app.dependency_overrides")
    
    # Vérifier que la fonction de dépendance est bien celle attendue
    logger.info(f"Fonction de dépendance dans app.dependency_overrides: {app.dependency_overrides.get('get_async_db_session')}")
    logger.info(f"Fonction de dépendance dans app.dependency_overrides (id): {id(app.dependency_overrides.get('get_async_db_session'))}")
    
    # Afficher toutes les dépendances actuellement surchargées
    logger.info(f"Dépendances actuellement surchargées: {app.dependency_overrides.keys()}")
    
    # Vérifier la configuration de l'application
    logger.info(f"Configuration de l'application: {app}")
    logger.info(f"Dépendances de l'application: {app.dependency_overrides}")
    
    # S'assurer que l'application FastAPI est correctement configurée
    if not hasattr(app, 'dependency_overrides'):
        app.dependency_overrides = {}
    
    # Surcharger les dépendances de base de données
    app.dependency_overrides.update({
        # Surcharge des dépendances asynchrones
        'get_async_db': override_async_db,
        'get_async_db_session': override_async_db_session,
        
        # Surcharge des dépendances synchrones
        'get_db': lambda: db_session.sync_session,
        'get_db_session': lambda: db_session.sync_session,
        
        # Surcharge du schéma OAuth2 pour les tests
        'oauth2_scheme': lambda: "test_token"
    })
    
    # Toutes les dépendances pointent maintenant vers app.db.get_async_db
    # Plus besoin de surcharger des dépendances spécifiques aux modules
    
    # Afficher les dépendances qui ont été surchargées avec leurs IDs
    logger.info("=== DÉPENDANCES SURCHARGÉES ===")
    for dep, override in list(app.dependency_overrides.items()):
        dep_name = getattr(dep, "__name__", str(dep))
        dep_module = getattr(dep, "__module__", "module inconnu")
        logger.info(f"- {dep_module}.{dep_name} (ID: {id(dep)}) -> {override}")
    
    # Vérifier que la session de test est bien configurée
    logger.info("\n=== CONFIGURATION DE LA SESSION DE TEST ===")
    logger.info(f"Type de la session de test: {type(db_session).__name__}")
    logger.info(f"ID de la session de test: {id(db_session)}")
    logger.info(f"Session de test active: {not db_session.in_transaction()}")
    yield
    
    # Nettoyer les surcharges
    app.dependency_overrides.clear()
    logger.info("Surcharges des dépendances nettoyées")


# Fixture pour le client de test asynchrone
@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Crée un client de test asynchrone FastAPI avec une base de données propre.
    
    - Utilise ASGITransport pour une intégration complète avec FastAPI
    - Ne surcharge plus les dépendances ici (c'est géré par override_dependencies)
    - Nettoie correctement après utilisation
    """
    # Ne plus surcharger get_async_db ici, c'est déjà fait par override_dependencies
    
    # Création du client de test asynchrone
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        try:
            yield client
        finally:
            # Nettoyage après le test
            await db_session.rollback()
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
