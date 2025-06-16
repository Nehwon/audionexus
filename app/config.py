"""
Configuration de l'application à partir des variables d'environnement.
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, AnyHttpUrl, validator

class Settings(BaseSettings):
    # Configuration de base
    PROJECT_NAME: str = "Gestionnaire d'Audiobooks"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changez-moi-en-production")
    API_V1_STR: str = "/api/v1"
    
    # Configuration CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    
    # Configuration de la base de données
    POSTGRES_SERVER: str = os.getenv("DB_HOST", "db")
    POSTGRES_USER: str = os.getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("DB_NAME", "audiobooks")
    DATABASE_URI: Optional[str] = None
    
    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    # Configuration JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changez-moi-aussi")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
    
    # Configuration des dossiers
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
    STATIC_FOLDER: str = os.path.join(BASE_DIR, "static")
    
    # Configuration Audiobookshelf
    ABS_API_URL: str = os.getenv("ABS_API_URL", "http://localhost:13378/api")
    ABS_USERNAME: str = os.getenv("ABS_USERNAME", "admin")
    ABS_PASSWORD: str = os.getenv("ABS_PASSWORD", "admin")
    
    class Config:
        case_sensitive = True

# Instance des paramètres
settings = Settings()

# Créer les dossiers nécessaires
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.STATIC_FOLDER, exist_ok=True)
