"""
Client pour interagir avec l'API VoidAuth (basée sur Keycloak).
"""
from typing import Optional, Dict, Any, List
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

class VoidAuthClient:
    """Client pour interagir avec l'API VoidAuth."""
    
    def __init__(self, server_url: str, realm: str, client_id: str, client_secret: str, 
                 admin_user: str, admin_password: str, verify_ssl: bool = True):
        """Initialise le client VoidAuth."""
        self.server_url = server_url.rstrip('/')
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.verify_ssl = verify_ssl
        self._keycloak_admin = None
        self._keycloak_openid = None
        self.realm_id = None
        
        # Initialisation du client Keycloak
        self._init_keycloak_client()
    
    def _init_keycloak_client(self):
        """Initialise le client Keycloak sous-jacent."""
        try:
            from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
            
            # Configuration de la connexion admin
            keycloak_connection = KeycloakOpenIDConnection(
                server_url=self.server_url,
                username=self.admin_user,
                password=self.admin_password,
                realm_name="master",
                client_id="admin-cli",
                verify=self.verify_ssl
            )
            
            # Initialisation du client admin
            self._keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
            self._keycloak_openid = self._keycloak_admin.keycloak_openid
            self.realm_id = self._keycloak_admin.get_realm(self.realm)["id"]
            
            logger.info(f"Client VoidAuth initialisé pour le realm '{self.realm}'")
            
        except ImportError:
            logger.error("Le module 'python-keycloak' est requis pour utiliser VoidAuth")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de VoidAuth: {str(e)}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe."""
        try:
            token = self._keycloak_openid.token(
                username=username,
                password=password,
                grant_type="password",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            return token
        except Exception as e:
            logger.warning(f"Échec de l'authentification pour {username}: {str(e)}")
            return None
