"""
Package pour la gestion de la base de données.

Ce module fournit une interface unifiée pour l'accès à la base de données,
que ce soit en mode synchrone ou asynchrone.
"""
import warnings
import logging
from typing import Any, Optional

# Configuration du logger
logger = logging.getLogger(__name__)

# Variables globales qui seront initialisées de manière différée
Base: Any = None
engine: Any = None
SessionLocal: Any = None
ScopedSession: Any = None
get_db: Any = None
get_async_db: Any = None
get_db_session: Any = None
get_async_db_session: Any = None
AsyncSessionLocal: Any = None
async_engine: Any = None
models: Any = None
_initialized: bool = False

def init_database() -> None:
    """
    Initialise la base de données de manière différée.
    
    Cette fonction doit être appelée explicitement après la configuration de l'application.
    Elle initialise les moteurs de base de données synchrones et asynchrones,
    ainsi que les sessions et les modèles.
    """
    global Base, engine, SessionLocal, ScopedSession, get_db, get_async_db, \
           get_db_session, get_async_db_session, AsyncSessionLocal, async_engine, \
           models, _initialized
    
    if _initialized:
        logger.debug("La base de données est déjà initialisée")
        return
    
    logger.info("Initialisation de la base de données...")
    
    try:
        # Import différé pour éviter les imports circulaires
        from .database import init_engine, Base as DatabaseBase, init_db, \
                              engine as db_engine, SessionLocal as db_SessionLocal, \
                              ScopedSession as db_ScopedSession
        from .session_manager import (
            init_async_engine,
            async_engine as db_async_engine,
            AsyncSessionLocal as db_AsyncSessionLocal,
            get_db as get_db_func,
            get_async_db as get_async_db_func,
            get_db_session as get_db_session_func,
            get_async_db_session as get_async_db_session_func
        )
        
        # Initialisation du moteur synchrone
        init_engine()
        
        # Initialisation du moteur asynchrone (ne fait que configurer, pas d'appel réseau)
        init_async_engine()
        
        # Initialisation des modèles
        from . import models as models_module
        
        # Création des tables (uniquement pour le moteur synchrone)
        init_db()
        
        # Assignation des références globales
        Base = DatabaseBase
        models = models_module
        
        # Configuration des sessions
        engine = db_engine
        SessionLocal = db_SessionLocal
        ScopedSession = db_ScopedSession
        async_engine = db_async_engine
        AsyncSessionLocal = db_AsyncSessionLocal
        
        # Configuration des fonctions d'aide
        get_db = get_db_func
        get_async_db = get_async_db_func
        get_db_session = get_db_session_func
        get_async_db_session = get_async_db_session_func
        
        _initialized = True
        logger.info("Base de données initialisée avec succès")
        
    except ImportError as e:
        logger.error(f"Erreur d'importation lors de l'initialisation de la base de données: {e}")
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'initialisation de la base de données: {e}")
        raise

__all__ = [
    'Base',
    'engine',
    'async_engine',
    'init_db',
    'init_async_engine',
    'get_db',
    'get_async_db',
    'get_db_session',
    'get_async_db_session',
    'AsyncSessionLocal',
    'SessionLocal',
    'ScopedSession',
    'models',
]
