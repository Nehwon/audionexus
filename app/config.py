"""
Configuration de l'application à partir des variables d'environnement.
"""
import os
import logging
from typing import List, Optional, Union, ClassVar
from pydantic import AnyHttpUrl, field_validator, Field, ConfigDict, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_bool(value: Union[str, bool]) -> bool:
    """Convertit une chaîne en booléen."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.split('#')[0].strip()  # Supprime les commentaires
    return str(value).lower() in ("true", "1", "t", "y", "yes")

def parse_int(value: Union[str, int], default: int = 0) -> int:
    """Convertit une chaîne en entier en gérant les commentaires et les erreurs."""
    if isinstance(value, int):
        return value
    try:
        # Supprime les commentaires et espaces, puis convertit en entier
        return int(str(value).split('#')[0].strip())
    except (ValueError, TypeError):
        return default

class Settings(BaseSettings):
    # Configuration de base
    PROJECT_NAME: str = Field(
        default="Gestionnaire d'Audiobooks",
        description="Nom de l'application"
    )
    DEBUG: bool = Field(
        default=parse_bool(os.getenv("DEBUG", "False")),
        description="Active le mode débogage"
    )
    TESTING: bool = Field(
        default=parse_bool(os.getenv("TESTING", "False")),
        description="Mode test (désactive certaines fonctionnalités comme l'initialisation automatique de la base de données)"
    )
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "changez-moi-en-production"),
        description="Clé secrète pour la signature des tokens JWT"
    )
    API_V1_STR: str = Field(
        default="/api/v1",
        description="Préfixe des routes API"
    )
    
    # Configuration CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    
    # Configuration de la base de données
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "audionexus")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "audionexus")
    DB_NAME: str = os.getenv("DB_NAME", "audionexus")
    DATABASE_URI: Optional[str] = None
    DATABASE_URI_SYNC: Optional[str] = None
    
    @field_validator("DATABASE_URI", mode='before')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: 'ValidationInfo') -> str:
        if isinstance(v, str) and v:
            return v
            
        values = info.data
        if os.getenv("TESTING", "").lower() == "true":
            # En mode test, on utilise SQLite en mémoire
            return "sqlite+aiosqlite:///:memory:"
            
        # En production/développement, on utilise MySQL avec le pilote asynchrone aiomysql
        return f"mysql+aiomysql://{values.get('DB_USER')}:{values.get('DB_PASSWORD')}@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}?charset=utf8mb4"
    
    @field_validator("DATABASE_URI_SYNC", mode='before')
    @classmethod
    def assemble_sync_db_connection(cls, v: Optional[str], info: 'ValidationInfo') -> str:
        if isinstance(v, str) and v:
            return v
            
        values = info.data
        if os.getenv("TESTING", "").lower() == "true":
            # En mode test, on utilise SQLite en mémoire
            return "sqlite:///:memory:"
            
        # URL de connexion synchrone pour l'initialisation
        return f"mysql+pymysql://{values.get('DB_USER')}:{values.get('DB_PASSWORD')}@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}?charset=utf8mb4"
    
    # Configuration JWT
    JWT_SECRET: str = Field(
        default=os.getenv("JWT_SECRET", "changez-moi-aussi"),
        description="Clé secrète pour les tokens JWT"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithme de signature JWT"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=parse_int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"), 10080),  # 7 jours par défaut
        description="Durée de validité du token d'accès en minutes"
    )
    
    # Configuration des dossiers
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
    STATIC_FOLDER: str = os.path.join(BASE_DIR, "static")
    
    # Configuration Audiobookshelf
    ABS_API_URL: str = os.getenv("ABS_API_URL", "http://localhost:13378/api")
    ABS_USERNAME: str = os.getenv("ABS_USERNAME", "admin")
    ABS_PASSWORD: str = os.getenv("ABS_PASSWORD", "admin")
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        json_schema_extra={
            "example": {
                "PROJECT_NAME": "Gestionnaire d'Audiobooks",
                "DEBUG": False,
                "API_V1_STR": "/api/v1"
            }
        }
    )

def clean_environment_variables():
    """Nettoie les variables d'environnement problématiques avant leur utilisation par Pydantic."""
    # Liste des variables à nettoyer
    vars_to_clean = ["ACCESS_TOKEN_EXPIRE_MINUTES"]
    
    for var_name in vars_to_clean:
        if var_name in os.environ:
            # Supprime les commentaires et espaces
            cleaned_value = os.environ[var_name].split('#')[0].strip()
            # Met à jour la variable d'environnement avec la valeur nettoyée
            os.environ[var_name] = cleaned_value
            logger.debug(f"Variable d'environnement nettoyée : {var_name}={cleaned_value}")

def get_settings() -> Settings:
    """
    Retourne l'instance des paramètres de configuration.
    
    Cette fonction permet de gérer correctement le rechargement des variables d'environnement
    lors des tests et nettoie les valeurs problématiques.
    """
    # En mode test, on force certaines valeurs et on nettoie les variables d'environnement problématiques
    if os.getenv("TESTING", "").lower() == "true":
        logger.info("Chargement de la configuration en mode TEST")
        
        # Nettoyage des variables d'environnement problématiques
        if "ACCESS_TOKEN_EXPIRE_MINUTES" in os.environ:
            logger.warning("Suppression de la variable d'environnement ACCESS_TOKEN_EXPIRE_MINUTES pour les tests")
            del os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
        
        # Chargement des paramètres avec des valeurs par défaut pour les tests
        return Settings(
            DEBUG=True,
            DATABASE_URI="sqlite+aiosqlite:///:memory:",
            ACCESS_TOKEN_EXPIRE_MINUTES=60,  # 1h pour les tests
            # Désactive le chargement des variables d'environnement
            _env_file=None,
            _env_file_encoding=None
        )
    
    # En mode production/développement, on nettoie les variables d'environnement avant utilisation
    clean_environment_variables()
    return Settings()

# Instance des paramètres
settings = get_settings()

# Créer les dossiers nécessaires
if not os.getenv("TESTING", "").lower() == "true":
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(settings.STATIC_FOLDER, exist_ok=True)
    logger.info("Dossiers de stockage initialisés")
