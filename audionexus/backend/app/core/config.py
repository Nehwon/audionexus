from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configuration de l'application
    PROJECT_NAME: str = "AudioNexus"
    VERSION: str = "0.3.1"
    API_V1_STR: str = "/api/v1"
    
    # Configuration de la base de données
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/audionexus"
    
    # Configuration JWT
    SECRET_KEY: str = "your-secret-key-here"  # À remplacer par une clé sécurisée en production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 jours
    
    # Configuration CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Configuration de l'email (pour la réinitialisation de mot de passe)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    
    # Premier administrateur
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Créer une instance des paramètres
settings = Settings()
