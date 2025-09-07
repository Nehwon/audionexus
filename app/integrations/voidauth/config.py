"""
Configuration pour l'intégration avec VoidAuth.
"""

import os
from typing import Any, Dict, Optional

from pydantic import BaseSettings, Field, validator


class VoidAuthConfig(BaseSettings):
    """Configuration pour l'intégration avec VoidAuth."""

    # URL du serveur VoidAuth (ex: http://localhost:8080)
    server_url: str = Field(..., env="VOIDAUTH_SERVER_URL")

    # Nom du royaume (realm) à utiliser
    realm: str = Field(..., env="VOIDAUTH_REALM")

    # ID du client OAuth2
    client_id: str = Field(..., env="VOIDAUTH_CLIENT_ID")

    # Secret du client OAuth2
    client_secret: str = Field(..., env="VOIDAUTH_CLIENT_SECRET")

    # Nom d'utilisateur administrateur
    admin_user: str = Field(..., env="VOIDAUTH_ADMIN_USER")

    # Mot de passe administrateur
    admin_password: str = Field(..., env="VOIDAUTH_ADMIN_PASSWORD")

    # Vérification SSL (désactiver en développement)
    verify_ssl: bool = Field(True, env="VOIDAUTH_VERIFY_SSL")

    # Timeout des requêtes en secondes
    timeout: int = Field(10, env="VOIDAUTH_TIMEOUT")

    # Configuration du token
    token_expire_minutes: int = Field(30, env="TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def dict(self) -> Dict[str, Any]:
        """Retourne la configuration sous forme de dictionnaire."""
        return {
            "server_url": self.server_url,
            "realm": self.realm,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "admin_user": self.admin_user,
            "admin_password": self.admin_password,
            "verify_ssl": self.verify_ssl,
            "timeout": self.timeout,
            "token_expire_minutes": self.token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
        }


def get_voidauth_config() -> VoidAuthConfig:
    """Retourne la configuration VoidAuth."""
    return VoidAuthConfig()
