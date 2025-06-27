"""
Gestion unifiée des sessions de base de données pour les modes synchrone et asynchrone.
"""
from typing import Generator, AsyncGenerator, Union, Optional
from contextlib import contextmanager, asynccontextmanager

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession as AsyncDBSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

# Configuration du moteur synchrone
from .database import engine, SessionLocal

# Variables globales qui seront initialisées par init_async_engine()
async_engine: Optional[AsyncEngine] = None
AsyncSessionLocal = None

def init_async_engine() -> None:
    """
    Initialise le moteur asynchrone et la session factory.
    
    Cette fonction doit être appelée après la configuration de l'application
    pour s'assurer que les paramètres de configuration sont correctement chargés.
    """
    global async_engine, AsyncSessionLocal
    
    from app.config import settings  # Import différé pour permettre la configuration des tests
    
    # Configuration du moteur asynchrone
    database_uri = settings.DATABASE_URI or "sqlite+aiosqlite:///:memory:"
    
    # Si c'est une URL PostgreSQL, s'assurer d'utiliser le bon dialecte
    if database_uri.startswith("postgresql://"):
        database_uri = database_uri.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Création du moteur
    async_engine = create_async_engine(
        database_uri,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    # Configuration de la session factory
    AsyncSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncDBSession,
        expire_on_commit=False
    )

# L'initialisation du moteur est maintenant gérée de manière différée
# via la fonction init_async_engine() appelée depuis app/db/__init__.py

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

async def get_async_db() -> AsyncGenerator[AsyncDBSession, None]:
    """
    Fournit une session de base de données asynchrone.
    
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

# Alias pour la rétrocompatibilité
get_async_db = get_async_db_session
