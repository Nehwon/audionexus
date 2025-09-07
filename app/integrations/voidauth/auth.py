"""
Gestion de l'authentification avec VoidAuth.
"""

import logging
from typing import Any, Dict, Optional

# Configuration du logger
logger = logging.getLogger(__name__)


class AuthManager:
    """Gestion de l'authentification avec VoidAuth."""

    def __init__(self, keycloak_openid, client_id: str, client_secret: str):
        """Initialise le gestionnaire d'authentification."""
        self._keycloak_openid = keycloak_openid
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe."""
        try:
            token = self._keycloak_openid.token(
                username=username,
                password=password,
                grant_type="password",
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
            return token
        except Exception as e:
            logger.warning(f"Échec de l'authentification pour {username}: {str(e)}")
            return None

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Rafraîchit un token d'accès."""
        try:
            token = self._keycloak_openid.refresh_token(
                refresh_token=refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
            return token
        except Exception as e:
            logger.warning(f"Échec du rafraîchissement du token: {str(e)}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un utilisateur à partir de son token d'accès."""
        try:
            user_info = self._keycloak_openid.userinfo(access_token)
            return user_info
        except Exception as e:
            logger.warning(
                f"Échec de la récupération des informations utilisateur: {str(e)}"
            )
            return None

    def introspect_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie la validité d'un token et retourne ses informations."""
        try:
            return self._keycloak_openid.introspect(token)
        except Exception as e:
            logger.warning(f"Échec de l'introspection du token: {str(e)}")
            return None

    def logout(self, refresh_token: str) -> bool:
        """Déconnecte un utilisateur en invalidant son refresh token."""
        try:
            self._keycloak_openid.logout(refresh_token)
            return True
        except Exception as e:
            logger.warning(f"Échec de la déconnexion: {str(e)}")
            return False
