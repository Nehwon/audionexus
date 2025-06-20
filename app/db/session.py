"""
Configuration de la session de base de données SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config import settings

# Création du moteur SQLAlchemy
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Session pour les requêtes asynchrones
ScopedSession = scoped_session(SessionLocal)

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
