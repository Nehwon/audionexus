"""
Configuration de l'application avec gestion unifiée des environnements.
Résoud les conflits entre SQLite (tests/dev) et MySQL (production).
"""
import os
import logging
from datetime import timedelta
from enum import Enum
from typing import Optional, Literal
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Types d'environnements supportés."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class DatabaseType(Enum):
    """Types de bases de données supportés."""
    SQLITE = "sqlite"
    MYSQL = "mysql"

class DatabaseSettings(BaseSettings):
    """Configuration de la base de données avec support SQLite/MySQL."""

    # Configuration de base
    type: DatabaseType = Field(default=DatabaseType.SQLITE)
    host: str = Field(default="localhost")
    port: Optional[int] = Field(default=None)
    user: str = Field(default="audionexus")
    password: str = Field(default="")
    name: str = Field(default="audionexus")
    database_uri: Optional[str] = Field(default=None)

    # Configuration SQLite
    sqlite_path: str = Field(default="./audionexus.db")

    # Configuration de connexion
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)
    pool_timeout: int = Field(default=30)
    pool_recycle: int = Field(default=3600)
    echo: bool = Field(default=False)

    class Config:
        env_prefix = ""
        env_nested_delimiter = "__"

    def get_database_uri(self) -> str:
        """Génère l'URI de connexion à la base de données."""
        if self.database_uri:
            return self.database_uri

        if self.type == DatabaseType.SQLITE:
            # En mode test, toujours utiliser la mémoire
            if os.getenv("TESTING", "").lower() == "true":
                return "sqlite+aiosqlite:///:memory:"
            # Sinon utiliser le fichier SQLite
            return f"sqlite+aiosqlite:///{self.sqlite_path}"

        elif self.type == DatabaseType.MYSQL:
            return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port or 3306}/{self.name}"

        else:
            raise ValueError(f"Type de base de données non supporté: {self.type}")

class Settings(BaseSettings):
    """Configuration unifiée de l'application."""

    # Configuration de base
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    testing: bool = Field(default=False)
    project_name: str = Field(default="AudioNexus")

    # Sécurité
    secret_key: str = Field(default="changez-moi-en-production")
    jwt_secret: str = Field(default="changez-moi-aussi")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=10080)  # 7 jours

    # Base de données (configuration imbriquée)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # URLs et CORS
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    api_v1_str: str = Field(default="/api/v1")

    # Audiobookshelf
    abs_api_url: str = Field(default="http://localhost:13378/api")
    abs_username: str = Field(default="admin")
    abs_password: str = Field(default="admin")

    # VoidAuth (OIDC)
    voidauth_server_url: str = Field(default="http://localhost:8080")
    voidauth_realm: str = Field(default="audionexus")
    voidauth_client_id: str = Field(default="audionexus-backend")
    voidauth_client_secret: str = Field(default="")
    voidauth_admin_user: str = Field(default="admin")
    voidauth_admin_password: str = Field(default="")

    # Stockage
    upload_folder: str = Field(default="./uploads")
    static_folder: str = Field(default="./static")

    # Configuration Pydantic
    model_config = SettingsConfigDict(
        env_prefix="",
        env_nested_delimiter="__",
        case_sensitive=False,
        validate_assignment=True,
    )

    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v):
        """Valide et convertit la valeur d'environnement."""
        if isinstance(v, str):
            v = v.lower()
            try:
                return Environment(v)
            except ValueError:
                raise ValueError(f"Environnement invalide: {v}")
        return v

    def get_database_uri(self) -> str:
        """Alias pour accéder facilement à l'URI de base de données."""
        return self.database.get_database_uri()

    def is_production(self) -> bool:
        """Vérifie si l'application est en mode production."""
        return self.environment == Environment.PRODUCTION

    def should_use_sqlite(self) -> bool:
        """Détermine si SQLite doit être utilisé."""
        return (
            self.testing or
            self.database.type == DatabaseType.SQLITE or
            self.environment == Environment.DEVELOPMENT
        )

    def get_pool_config(self) -> dict:
        """Retourne la configuration de pool appropriée selon le type de DB."""
        base_config = {
            'pool_pre_ping': True,
            'pool_recycle': self.database.pool_recycle,
            'pool_timeout': self.database.pool_timeout,
            'echo': self.database.echo,
        }

        if self.database.type == DatabaseType.SQLITE:
            base_config.update({
                'poolclass': None if ':memory:' in self.get_database_uri() else None,
                'connect_args': {'check_same_thread': False},
            })
        elif self.database.type == DatabaseType.MYSQL:
            base_config.update({
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
            })

        return base_config
        return base_config

    @property
    def PROJECT_NAME(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.project_name

    @property
    def API_V1_STR(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.api_v1_str

    @property
    def SECRET_KEY(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.secret_key

    @property
    def JWT_SECRET_KEY(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.jwt_secret

    @property
    def DEBUG(self) -> bool:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.debug

    @property
    def TESTING(self) -> bool:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.testing

    @property
    def BACKEND_CORS_ORIGINS(self) -> list[str]:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.backend_cors_origins

    @property
    def STATIC_FOLDER(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.static_folder

    @property
    def UPLOAD_FOLDER(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.upload_folder

    @property
    def DATABASE_URI(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.get_database_uri()

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.access_token_expire_minutes

    @property
    def JWT_ALGORITHM(self) -> str:
        """Propriété de compatibilité pour les anciennes références en majuscules."""
        return self.jwt_algorithm

@lru_cache()
def get_settings() -> Settings:
    """Fonction factory pour obtenir l'instance des paramètres."""
    # Configuration selon l'environnement
    env = os.getenv("ENVIRONMENT", "development").lower()
    testing = os.getenv("TESTING", "").lower() == "true"

    if testing:
        # Configuration pour les tests - toujours SQLite en mémoire
        return Settings(
            environment=Environment.TESTING,
            testing=True,
            debug=True,
            database=DatabaseSettings(type=DatabaseType.SQLITE),
            access_token_expire_minutes=60,  # 1 heure pour les tests
            # Ajouter tous les attributs manquants pour les tests
            project_name="AudioNexus Test",
        )
    elif env == "production":
        # Production - MySQL obligatoire
        return Settings(
            environment=Environment.PRODUCTION,
            debug=False,
            database=DatabaseSettings(type=DatabaseType.MYSQL),
        )
    else:
        # Développement - SQLite par défaut
        return Settings(
            environment=Environment.DEVELOPMENT,
            debug=True,
            database=DatabaseSettings(type=DatabaseType.SQLITE),
        )

# Instance globale des paramètres
settings = get_settings()

# Log de la configuration actuelle
logger.info(f"Configuration chargée: {settings.environment.value}")
logger.info(f"Type de base de données: {settings.database.type.value}")
logger.info(f"URI de base de données: {settings.get_database_uri()}")


class Config:
    """Classe de configuration Flask compatible avec les settings unifiés."""

    # Configuration de base
    SECRET_KEY = settings.secret_key
    TESTING = settings.testing
    DEBUG = settings.debug

    # JWT
    JWT_SECRET_KEY = settings.jwt_secret
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=settings.access_token_expire_minutes)

    # Base de données
    SQLALCHEMY_DATABASE_URI = settings.get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = settings.database.echo

    # Pool configuration
    SQLALCHEMY_POOL_SIZE = settings.database.pool_size if hasattr(settings.database, 'pool_size') else None
    SQLALCHEMY_MAX_OVERFLOW = settings.database.max_overflow if hasattr(settings.database, 'max_overflow') else None
    SQLALCHEMY_POOL_TIMEOUT = settings.database.pool_timeout if hasattr(settings.database, 'pool_timeout') else None
    SQLALCHEMY_POOL_RECYCLE = settings.database.pool_recycle if hasattr(settings.database, 'pool_recycle') else None
    SQLALCHEMY_POOL_PRE_PING = True

    # CORS
    CORS_ORIGINS = settings.backend_cors_origins

    # VoidAuth (OIDC)
    VOIDAUTH_SERVER_URL = settings.voidauth_server_url
    VOIDAUTH_REALM = settings.voidauth_realm
    VOIDAUTH_CLIENT_ID = settings.voidauth_client_id
    VOIDAUTH_CLIENT_SECRET = settings.voidauth_client_secret
    VOIDAUTH_ADMIN_USER = settings.voidauth_admin_user
    VOIDAUTH_ADMIN_PASSWORD = settings.voidauth_admin_password

    # Répertoires
    UPLOAD_FOLDER = settings.upload_folder
    STATIC_FOLDER = settings.static_folder

    # Suppression des emails pour les tests
    MAIL_SUPPRESS_SEND = True
