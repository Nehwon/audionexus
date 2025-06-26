"""
Configuration et gestion de la base de données SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

from app.config import settings

# Déclaration de la base pour les modèles SQLAlchemy
# Cette instance unique de Base sera utilisée dans tout le projet
Base = declarative_base()

# Import des modèles pour s'assurer qu'ils sont enregistrés avec la Base
# L'import doit être fait après la déclaration de Base
from app.db.models.base import *  # noqa: F401, F403

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
    # Utilisation de l'instance unique de Base importée au début du fichier
    Base.metadata.create_all(bind=engine)
