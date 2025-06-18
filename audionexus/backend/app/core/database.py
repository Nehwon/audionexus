from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# URL de connexion à la base de données
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Création du moteur SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles
Base = declarative_base()

def get_db():
    """
    Fournit une session de base de données pour chaque requête.
    La session est automatiquement fermée après utilisation.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialise la base de données en créant toutes les tables.
    À utiliser avec précaution en production.
    """
    Base.metadata.create_all(bind=engine)
    
    # Créer l'utilisateur admin si nécessaire
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.services.auth import AuthService
        
        admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        if not admin:
            user_in = {
                "email": settings.FIRST_SUPERUSER_EMAIL,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
                "full_name": "Admin",
                "is_superuser": True,
                "is_active": True
            }
            AuthService.create_user(db, user_in)
            print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()
