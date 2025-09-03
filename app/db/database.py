"""
Configuration et gestion de la base de données SQLAlchemy.
"""
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

# Déclaration de la base pour les modèles SQLAlchemy
# Cette instance unique de Base sera utilisée dans tout le projet
Base = declarative_base()

# Variables globales qui seront initialisées par init_engine()
engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker] = None
ScopedSession = None

def init_engine() -> None:
    """
    Initialise le moteur de base de données et les sessions.
    
    Cette fonction doit être appelée après la configuration de l'application
    pour s'assurer que les paramètres de configuration sont correctement chargés.
    """
    global engine, SessionLocal, ScopedSession
    
    # Import différé pour permettre la configuration des tests
    from app.config import settings
    
    # Configuration de l'URL de la base de données
    database_uri = settings.get_database_uri()
    
    # Détection du type de base de données
    is_sqlite = database_uri.startswith('sqlite')
    is_mysql = 'mysql' in database_uri
    
    # Paramètres communs
    engine_kwargs: Dict[str, Any] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'echo': settings.debug,  # Afficher les requêtes SQL en mode debug
    }
    
    # Configuration spécifique pour les tests (SQLite en mémoire)
    if is_sqlite and ':memory:' in database_uri:
        engine_kwargs.update({
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,  # Utiliser un pool statique pour SQLite en mémoire
            'echo': settings.debug,
        })
    # Paramètres spécifiques à MySQL
    elif is_mysql:
        engine_kwargs.update({
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'connect_args': {
                'connect_timeout': 10,
                'charset': 'utf8mb4',
            }
        })
    # Paramètres spécifiques à PostgreSQL (conservés pour référence)
    elif not is_sqlite:
        engine_kwargs.update({
            'pool_size': 20,
            'max_overflow': 10,
            'pool_timeout': 30,
        })
    else:
        # Paramètres spécifiques à SQLite
        engine_kwargs.update({
            'connect_args': {'check_same_thread': False},
        })
    
    # Création du moteur avec connect_args pour SQLite si nécessaire
    if is_sqlite:
        engine_kwargs.setdefault('connect_args', {'check_same_thread': False})
    
    # Désactiver le pool pour SQLite en mémoire
    if database_uri == 'sqlite+aiosqlite:///:memory:':
        engine_kwargs['poolclass'] = StaticPool
        engine_kwargs['connect_args'] = {'check_same_thread': False}
    
    # Création du moteur
    engine = create_engine(database_uri, **engine_kwargs)
    
    # Configuration de la session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    ScopedSession = scoped_session(SessionLocal)
    
    # Import des modèles pour s'assurer qu'ils sont enregistrés avec la Base
    # L'import doit être fait après la déclaration de Base et l'initialisation du moteur
    # noqa pour éviter les avertissements sur les imports non utilisés
    import app.db.models.base  # noqa: F401

# Initialisation différée du moteur
# Ne pas initialiser automatiquement pour permettre la configuration des tests
try:
    from app.config import settings
    if not settings.testing:  # Ne pas initialiser en mode test
        init_engine()
except ImportError:
    # En cas d'erreur d'import, initialiser normalement
    init_engine()

def get_db():
    """
    Fournit une session de base de données pour les dépendances FastAPI.
    
    Yields:
        Session: Une session de base de données
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """
    Initialise la base de données en créant toutes les tables.
    Gère à la fois les moteurs synchrones et asynchrones.
    """
    from sqlalchemy.ext.asyncio import AsyncEngine
    
    if isinstance(engine, AsyncEngine):
        # Pour un moteur asynchrone, on utilise run_sync
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        # Pour un moteur synchrone, on utilise directement create_all
        Base.metadata.create_all(bind=engine)
