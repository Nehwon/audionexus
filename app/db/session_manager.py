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
    
    # Utiliser l'URI fournie ou celle des paramètres
    if database_uri is None:
        database_uri = settings.DATABASE_URI or "sqlite+aiosqlite:///:memory:"
    
    # En mode test, forcer SQLite en mémoire
    if os.getenv("TESTING", "").lower() == "true":
        database_uri = "sqlite+aiosqlite:///:memory:"
        logger.info(f"Forçage de l'utilisation de SQLite en mémoire pour les tests: {database_uri}")
    
    # Si c'est une URL PostgreSQL, s'assurer d'utiliser le bon dialecte
    if database_uri.startswith("postgresql://"):
        database_uri = database_uri.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    logger.info(f"Initialisation du moteur asynchrone avec l'URI: {database_uri}")
    
    # Configuration spécifique pour SQLite
    connect_args = {}
    if "sqlite" in database_uri:
        connect_args = {"check_same_thread": False}
    
    # Création du moteur
    engine = create_async_engine(
        database_uri,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args=connect_args
    )
    
    # Assigner le moteur à la variable globale
    async_engine = engine
    
    # Configuration de la session factory
    AsyncSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncDBSession,
        expire_on_commit=False
    )
    
    logger.info("Moteur asynchrone initialisé avec succès")

# Initialisation différée du moteur
# On ne l'initialise plus automatiquement au chargement du module
# pour permettre une configuration personnalisée dans les tests

def get_db() -> Generator[Session, None, None]:
    """
    Fournit une session de base de données synchrone.
    
    À utiliser dans les endpoints FastAPI avec `Depends(get_db)`.
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

# Fonction pour FastAPI
async def get_async_db() -> AsyncGenerator[AsyncDBSession, None]:
    """
    Fournit une session de base de données asynchrone pour FastAPI.
    
    À utiliser dans les endpoints FastAPI avec `Depends(get_async_db)`.
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
