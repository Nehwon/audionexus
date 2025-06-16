"""
Configuration et gestion de la base de données SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config import settings

# Création du moteur SQLAlchemy
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URI or \
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_timeout=30,
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Session pour les requêtes asynchrones
ScopedSession = scoped_session(SessionLocal)

# Base pour les modèles
Base = declarative_base()

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

def init_db():
    """
    Initialise la base de données en créant toutes les tables.
    """
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
