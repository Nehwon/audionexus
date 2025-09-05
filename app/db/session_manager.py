"""
Gestion unifiée des sessions de base de données pour les modes synchrone et asynchrone.
"""
import logging
import os
from typing import Generator, AsyncGenerator, Union, Optional
from contextlib import contextmanager, asynccontextmanager

# Configuration du logger
logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession as AsyncDBSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from sqlalchemy.pool import StaticPool

# Configuration du moteur synchrone
from .database import engine, SessionLocal

# Variables globales qui seront initialisées par init_async_engine()
async_engine: Optional[AsyncEngine] = None
AsyncSessionLocal = None

def init_async_engine(database_uri: str = None, force: bool = False) -> None:
    """
    Initialise le moteur asynchrone et la session factory.

    Args:
        database_uri: URI de la base de données à utiliser (optionnel)
        force: Force la réinitialisation du moteur même s'il existe déjà
    """
    global async_engine, AsyncSessionLocal

    # Ne pas réinitialiser si le moteur existe déjà et qu'on ne force pas
    if async_engine is not None and not force:
        return

    from app.config import settings  # Import différé pour permettre la configuration des tests

    # Utiliser l'URI fournie ou celle des paramètres unifiés
    if database_uri is None:
        database_uri = settings.get_database_uri()

    logger.info(f"Initialisation du moteur asynchrone avec l'URI: {database_uri}")
    logger.info(f"Environnement: {settings.environment.value}, Testing: {settings.testing}")

    # Configuration spécifique selon le type de base de données
    connect_args = {}

    # Configuration unifiée des arguments d'engine
    engine_kwargs = {
        'echo': settings.database.echo,
        'pool_pre_ping': True,
        'pool_recycle': settings.database.pool_recycle,
    }

    # Configuration spécifique selon le type de base de données
    if settings.database.type == settings.database.type.__class__.SQLITE:
        engine_kwargs.update({
            'connect_args': {"check_same_thread": False},
        })

        # Configuration du pool pour SQLite en mémoire (tests)
        if ":memory:" in database_uri:
            engine_kwargs['poolclass'] = StaticPool

    # Configuration pour MySQL
    elif settings.database.type == settings.database.type.__class__.MYSQL:
        engine_kwargs.update({
            'pool_size': settings.database.pool_size,
            'max_overflow': settings.database.max_overflow,
            'pool_timeout': settings.database.pool_timeout,
        })
    else:
        raise ValueError(f"Type de base de données non supporté: {settings.database.type}")

    # Création du moteur unifié
    async_engine = create_async_engine(database_uri, **engine_kwargs)

    # Configuration de la session factory
    AsyncSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncDBSession,
        expire_on_commit=False
    )

    logger.info(f"Moteur asynchrone initialisé avec succès pour {settings.database.type.value}")

# Initialisation différée du moteur
# On ne l'initialise plus automatiquement au chargement du module
# pour permettre une configuration personnalisée dans les tests

def get_db() -> Generator[Session, None, None]:
    """
    Fournit une session de base de données synchrone.

    À utiliser dans les endpoints FastAPI avec `Depends(get_db)`.
    NOTE SYNCHRONE: Préférer les sessions async avec get_async_db() pour les nouvelles implémentations.
    Cette fonction reste disponible pour la rétrocompatibilité.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Fournit une session de base de données synchrone en tant que gestionnaire de contexte.
    
    À utiliser dans du code synchrone avec `with get_db_session() as db:`.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncDBSession, None]:
    """
    Fournit une session de base de données asynchrone en tant que gestionnaire de contexte.
    
    À utiliser dans du code asynchrone avec `async with get_async_db_session() as db:`.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# FONCTION CANONIQUE UNIQUE pour les sessions ASYNC
# Toutes les autres définitions de get_async_db() doivent être supprimées
# Utilisez toujours from app.db import get_async_db
async def get_async_db() -> AsyncGenerator[AsyncDBSession, None]:
    """
    Fournit une session de base de données asynchrone pour FastAPI.

    À utiliser dans les endpoints FastAPI avec `Depends(get_async_db)`.
    IMPORTANT: Cette est la seule et unique définition officielle de get_async_db()
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Le moteur asynchrone n'a pas été initialisé. Appelez init_async_engine() d'abord.")
        
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
