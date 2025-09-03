"""
Package pour la gestion de la base de données.

Ce module fournit une interface unifiée pour l'accès à la base de données
avec support pour FastAPI et SQLAlchemy 2.0 asynchrone.
"""
import logging
from typing import Any, Optional

# Configuration du logger
logger = logging.getLogger(__name__)

# Variables globales qui seront initialisées
Base = None
engine = None
SessionLocal = None
async_engine = None
AsyncSessionLocal = None
get_db = None
get_async_db = None
get_db_session = None
get_async_db_session = None

# Compatibilité avec l'ancienne architecture Flask
db = None
# Import de la base de données depuis database.py
try:
    from .database import Base, engine, SessionLocal
    logger.debug("Import de la base de données synchrone réussi")
except ImportError as e:
    logger.warning(f"Impossible d'importer la base de données synchrone: {e}")

# Import différé des fonctions asynchrones depuis session_manager.py
try:
    from .session_manager import (
        get_db,
        get_db_session,
        get_async_db,
        get_async_db_session,
        AsyncSessionLocal,
        async_engine,
        init_async_engine
    )
    logger.debug("Import des fonctions de session réussi")
except ImportError as e:
    logger.warning(f"Impossible d'importer les fonctions de session: {e}")

# Fonction d'initialisation simplifiée
def init_database():
    """
    Initialise la base de données et ses composants asynchrones.
    """
    try:
        from .database import init_engine
        from .session_manager import init_async_engine

        # Initialisation du moteur synchrone
        init_engine()

        # Initialisation du moteur asynchrone
        init_async_engine()

        logger.info("✅ Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise

# Fonction de compatibilité Flask (temporaire)
def init_app(app):
    """
    Fonction de compatibilité pour l'ancienne architecture Flask.
    Ne fait rien pour l'instant.
    """
    logger.info("⚠️  Fonction init_app appelée (compatibilité Flask) - aucune action")
    return None

# Alias pour la compatibilité
init_db = init_database

# Exports
__all__ = [
    # Base de données
    'Base',
    'engine',
    'SessionLocal',

    # Synchrone (session_manager)
    'get_db',
    'get_db_session',

    # Asynchrone
    'async_engine',
    'AsyncSessionLocal',
    'get_async_db',
    'get_async_db_session',

    # Compatibilité Flask
    'db',

    # Fonctions d'initialisation
    'init_app',  # Compatibilité Flask
    'init_database',
    'init_db',
    'init_async_engine',
]
