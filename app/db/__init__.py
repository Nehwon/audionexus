"""
Package pour la gestion de la base de données.

Ce module fournit une interface unifiée pour l'accès à la base de données,
que ce soit en mode synchrone ou asynchrone.
"""
import warnings
import logging
from typing import Any, Optional, TypeVar, Type, Dict, Callable, Awaitable, Union, List, cast

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
        from sqlalchemy.orm import declarative_base
        from .database import init_engine, Base as DatabaseBase, engine as db_engine, \
                            SessionLocal as db_SessionLocal, ScopedSession as db_ScopedSession
        from .session_manager import (
            get_db as get_db_func, 
            get_async_db as get_async_db_func,
            get_db_session as get_db_session_func,
            get_async_db_session as get_async_db_session_func,
            async_engine as db_async_engine,
            AsyncSessionLocal as db_AsyncSessionLocal,
            init_async_engine
        )
        
        # Initialisation des moteurs
        init_engine()
        init_async_engine()
        
        # Assignation des références globales
        Base = DatabaseBase
        from . import models as models_module
        models = models_module
        
        # Initialisation des sessions
        engine = db_engine
        SessionLocal = db_SessionLocal
        ScopedSession = db_ScopedSession
        async_engine = db_async_engine
        AsyncSessionLocal = db_AsyncSessionLocal
        
        # Initialisation des fonctions d'aide
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
        
    try:
        from .database import Base as BaseImport, engine as engine_import
        from .database import SessionLocal as SessionLocalImport, ScopedSession as ScopedSessionImport
        from .session_manager import (
            get_db as get_db_import,
            get_async_db as get_async_db_import,
            get_db_session as get_db_session_import,
            get_async_db_session as get_async_db_session_import,
            AsyncSessionLocal as AsyncSessionLocalImport,
            async_engine as async_engine_import,
            init_async_engine
        )
        from . import models as models_import
        
        # Initialisation du moteur asynchrone uniquement
        init_async_engine()
        
        # Mise à jour des références globales
        Base = BaseImport
        engine = engine_import
        SessionLocal = SessionLocalImport
        ScopedSession = ScopedSessionImport
        get_db = get_db_import
        get_async_db = get_async_db_import
        get_db_session = get_db_session_import
        get_async_db_session = get_async_db_session_import
        AsyncSessionLocal = AsyncSessionLocalImport
        async_engine = async_engine_import
        models = models_import
        _initialized = True
        
        # Initialisation différée de la base de données
        # Note: L'initialisation complète se fera au premier accès via les dépendances FastAPI
        # pour éviter les problèmes de boucle d'événements et de coroutines
        logger.info("L'initialisation de la base de données sera effectuée au premier accès via les dépendances FastAPI")
        
    except ImportError as e:
        warnings.warn(f"Erreur lors de l'initialisation différée de la base de données: {e}")
        # Les variables globales restent à None en cas d'erreur

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
