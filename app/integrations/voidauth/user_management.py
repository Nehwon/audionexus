"""
Gestion des utilisateurs pour l'intégration avec VoidAuth.
"""
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

# Configuration du logger
logger = logging.getLogger(__name__)

class UserManager:
    """Gestion des utilisateurs dans VoidAuth."""
    
    def __init__(self, keycloak_admin):
        """Initialise le gestionnaire d'utilisateurs."""
        self._keycloak_admin = keycloak_admin
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Crée un nouvel utilisateur."""
        try:
            # Préparation des données utilisateur
            user_rep = {
                'username': user_data['username'],
                'email': user_data['email'],
                'enabled': user_data.get('enabled', True),
                'emailVerified': user_data.get('email_verified', False),
                'credentials': [{
                    'type': 'password',
                    'value': user_data['password'],
                    'temporary': False
                }]
            }
            
            # Ajout des champs optionnels
            if 'first_name' in user_data:
                user_rep['firstName'] = user_data['first_name']
            if 'last_name' in user_data:
                user_rep['lastName'] = user_data['last_name']
            if 'attributes' in user_data:
                user_rep['attributes'] = user_data['attributes']
            
            # Création de l'utilisateur
            user_id = self._keycloak_admin.create_user(user_rep)
            logger.info(f"Utilisateur créé avec succès: {user_data['username']} (ID: {user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"Échec de la création de l'utilisateur {user_data.get('username')}: {str(e)}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Met à jour un utilisateur existant."""
        try:
            self._keycloak_admin.update_user(user_id, user_data)
            logger.info(f"Utilisateur mis à jour avec succès: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Échec de la mise à jour de l'utilisateur {user_id}: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Supprime un utilisateur."""
        try:
            self._keycloak_admin.delete_user(user_id)
            logger.info(f"Utilisateur supprimé avec succès: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Échec de la suppression de l'utilisateur {user_id}: {str(e)}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son ID."""
        try:
            return self._keycloak_admin.get_user(user_id)
        except Exception as e:
            logger.warning(f"Utilisateur non trouvé: {user_id} - {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son nom d'utilisateur."""
        users = self._keycloak_admin.get_users({"username": username})
        return users[0] if users else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son adresse email."""
        users = self._keycloak_admin.get_users({"email": email})
        return users[0] if users else None
    
    def set_user_password(self, user_id: str, password: str, temporary: bool = False) -> bool:
        """Définit le mot de passe d'un utilisateur."""
        try:
            self._keycloak_admin.set_user_password(user_id, password, temporary)
            logger.info(f"Mot de passe défini pour l'utilisateur {user_id}")
            return True
        except Exception as e:
            logger.error(f"Échec de la définition du mot de passe pour l'utilisateur {user_id}: {str(e)}")
            return False
    
    def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère les rôles d'un utilisateur."""
        try:
            return self._keycloak_admin.get_realm_roles_of_user(user_id)
        except Exception as e:
            logger.error(f"Échec de la récupération des rôles pour l'utilisateur {user_id}: {str(e)}")
            return []
    
    def add_user_roles(self, user_id: str, roles: List[str]) -> bool:
        """Ajoute des rôles à un utilisateur."""
        try:
            # Récupérer les objets de rôle complets
            all_roles = self._keycloak_admin.get_realm_roles()
            roles_to_add = [role for role in all_roles if role['name'] in roles]
            
            if roles_to_add:
                self._keycloak_admin.assign_realm_roles(user_id, roles_to_add)
                logger.info(f"Rôles ajoutés à l'utilisateur {user_id}: {', '.join(roles)}")
            return True
        except Exception as e:
            logger.error(f"Échec de l'ajout des rôles à l'utilisateur {user_id}: {str(e)}")
            return False
    
    def remove_user_roles(self, user_id: str, roles: List[str]) -> bool:
        """Supprime des rôles d'un utilisateur."""
        try:
            # Récupérer les objets de rôle complets
            all_roles = self._keycloak_admin.get_realm_roles()
            roles_to_remove = [role for role in all_roles if role['name'] in roles]
            
            if roles_to_remove:
                self._keycloak_admin.delete_realm_roles_of_user(user_id, roles_to_remove)
                logger.info(f"Rôles supprimés de l'utilisateur {user_id}: {', '.join(roles)}")
            return True
        except Exception as e:
            logger.error(f"Échec de la suppression des rôles de l'utilisateur {user_id}: {str(e)}")
            return False
