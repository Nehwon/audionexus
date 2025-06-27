import os
from pathlib import Path
from typing import List, Optional, Any

from pydantic import Field, field_validator, model_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configuration de l'application
    PROJECT_NAME: str = "AudioNexus"
    VERSION: str = "0.3.1"
    API_V1_STR: str = "/api/v1"
    
    # Configuration de la base de données
    DATABASE_URL: str = "mysql+aiomysql://audionexus:audionexus@db:3306/audionexus"
    
    # Configuration JWT
    SECRET_KEY: str = Field(
        default="your-secret-key-here",  # À remplacer par une clé sécurisée en production
        min_length=32,
        description="Clé secrète pour la signature des jetons JWT"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 jours
    
    # Configuration CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
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
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=os.path.join(Path(__file__).parent.parent.parent.parent, ".env"),
        env_file_encoding='utf-8',
        extra='ignore',
        env_nested_delimiter='__',
        validate_default=True
    )
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @field_validator('SECRET_KEY', mode='before')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("La clé secrète doit faire au moins 32 caractères")
        return v

# Créer une instance des paramètres
settings = Settings()
