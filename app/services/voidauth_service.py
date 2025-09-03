"""
Service pour gérer les opérations d'authentification avec VoidAuth.
"""
from typing import Dict, Optional, List
from fastapi import HTTPException, status
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakGetError, KeycloakPostError

from app.config import settings

class VoidAuthService:
    """
    Service pour interagir avec l'API VoidAuth (basée sur Keycloak).
    """
    
    def __init__(self):
        self.server_url = settings.voidauth_server_url
        self.realm = settings.voidauth_realm
        self.client_id = settings.voidauth_client_id
        self.client_secret = settings.voidauth_client_secret
        self.admin_username = settings.voidauth_admin_user
        self.admin_password = settings.voidauth_admin_password
        
        # Initialisation du client admin
        self.admin_client = self._get_admin_client()
        # Initialisation du client OIDC
        self.oidc_client = KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm,
            client_secret_key=self.client_secret
        )
    
    def _get_admin_client(self) -> KeycloakAdmin:
        """Initialise et retourne le client administrateur Keycloak."""
        try:
            return KeycloakAdmin(
                server_url=self.server_url,
                username=self.admin_username,
                password=self.admin_password,
                realm_name="master",  # Le royaume master pour l'admin
                verify=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Impossible de se connecter à l'API d'administration VoidAuth: {str(e)}"
            )
    
    async def create_user(self, username: str, email: str, password: str, **kwargs) -> Dict:
        """
        Crée un nouvel utilisateur dans VoidAuth.
        
        Args:
            username: Nom d'utilisateur
            email: Adresse email
            password: Mot de passe
            **kwargs: Autres attributs utilisateur (first_name, last_name, etc.)
            
        Returns:
            Dict: Informations sur l'utilisateur créé
        """
        try:
            # Vérifier si l'utilisateur existe déjà
            users = self.admin_client.get_users({"username": username, "email": email})
            if users:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Un utilisateur avec ce nom d'utilisateur ou cet email existe déjà"
                )
            
            # Créer l'utilisateur
            user_id = self.admin_client.create_user({
                "username": username,
                "email": email,
                "enabled": True,
                "emailVerified": False,  # L'email devra être vérifié
                "credentials": [{"value": password, "type": "password", "temporary": False}],
                **kwargs
            })
            
            # Récupérer les informations de l'utilisateur créé
            user = self.admin_client.get_user(user_id)
            return user
            
        except KeycloakPostError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
            )
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe.
        
        Args:
            username: Nom d'utilisateur ou email
            password: Mot de passe
            
        Returns:
            Optional[Dict]: Les tokens d'authentification ou None si l'authentification échoue
        """
        try:
            # Obtenir les tokens avec le flux de mot de passe
            tokens = self.oidc_client.token(
                username=username,
                password=password,
                grant_type="password"
            )
            return tokens
            
        except Exception as e:
            # L'authentification a échoué
            return None
    
    async def get_user_info(self, access_token: str) -> Dict:
        """
        Récupère les informations d'un utilisateur à partir de son token d'accès.
        
        Args:
            access_token: Token d'accès JWT
            
        Returns:
            Dict: Informations sur l'utilisateur
        """
        try:
            user_info = self.oidc_client.userinfo(access_token)
            return user_info
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token d'accès invalide ou expiré"
            )
    
    async def get_user_roles(self, user_id: str) -> List[str]:
        """
        Récupère les rôles d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur dans VoidAuth
            
        Returns:
            List[str]: Liste des noms de rôles
        """
        try:
            # Récupérer les rôles du client pour l'utilisateur
            client_roles = self.admin_client.get_client_roles_of_user(
                user_id=user_id,
                client_id=self.admin_client.get_client_id(self.client_id)
            )
            
            # Récupérer les rôles du royaume pour l'utilisateur
            realm_roles = self.admin_client.get_realm_roles_of_user(user_id)
            
            # Fusionner et retourner les noms de rôles uniques
            return list({role['name'] for role in client_roles + realm_roles})
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la récupération des rôles: {str(e)}"
            )
    
    async def reset_password(self, user_id: str, new_password: str) -> bool:
        """
        Réinitialise le mot de passe d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            new_password: Nouveau mot de passe
            
        Returns:
            bool: True si la réinitialisation a réussi
        """
        try:
            self.admin_client.set_user_password(
                user_id=user_id,
                password=new_password,
                temporary=False
            )
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur lors de la réinitialisation du mot de passe: {str(e)}"
            )

# Instance du service pour une utilisation facile
voidauth_service = VoidAuthService()
