"""
Configuration de la session de base de données SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import settings

# Vérification du type de base de données
is_sqlite = settings.DATABASE_URI and "sqlite" in settings.DATABASE_URI
is_mysql = settings.DATABASE_URI and "mysql" in settings.DATABASE_URI

# Configuration du moteur SQLAlchemy
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": settings.DEBUG,  # Afficher les requêtes SQL en mode debug
}

if is_mysql:
    # Configuration spécifique à MySQL
    engine_kwargs.update(
        {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "connect_args": {
                "connect_timeout": 10,
                "charset": "utf8mb4",
            },
        }
    )
elif not is_sqlite:
    # Ancienne configuration PostgreSQL (conservée pour référence)
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
        }
    )
else:
    # Configuration spécifique à SQLite
    engine_kwargs.update(
        {
            "poolclass": None,  # Désactive le pool de connexions
            "connect_args": {"check_same_thread": False},
        }
    )

# Création du moteur SQLAlchemy
engine = create_engine(settings.DATABASE_URI, **engine_kwargs)

"""
Module de compatibilité pour la gestion des sessions de base de données.

CORRECTION_IMPORTANTE: Ce module peut causer des conflits 'kw' dans FastAPI
à cause des définitions multiples de get_db(). Toujours importer depuis
app.db.session_manager directement pour éviter les erreurs 500/422.

Ce module est maintenu uniquement pour la rétrocompatibilité.
Pour les nouvelles implémentations, utilisez directement `app.db.session_manager`.
"""
import warnings
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .database import SessionLocal
from .session_manager import (
    AsyncSessionLocal,
)
from .session_manager import get_async_db as _get_async_db
from .session_manager import get_async_db_session as _get_async_db_session
from .session_manager import get_db as _get_db
from .session_manager import get_db_session as _get_db_session

# Avertissement de dépréciation
warnings.warn(
    "Le module 'app.db.session' est déprécié. Utilisez 'app.db.session_manager' à la place.",
    DeprecationWarning,
    stacklevel=2,
)

# Alias pour la rétrocompatibilité
get_db = _get_db
get_async_db = _get_async_db
get_db_session = _get_db_session
get_async_db_session = _get_async_db_session
