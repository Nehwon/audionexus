"""
Factory pour créer et gérer les instances du client VoidAuth.
"""
from typing import Optional
import logging

from .client import VoidAuthClient
from .config import get_voidauth_config

# Configuration du logger
logger = logging.getLogger(__name__)

# Instance singleton du client VoidAuth
_voidauth_client = None

def get_voidauth_client() -> Optional[VoidAuthClient]:
    """
    Retourne une instance du client VoidAuth.
    
    Cette fonction implémente le pattern Singleton pour s'assurer qu'une seule
    instance du client est utilisée dans toute l'application.
    
    Returns:
        Une instance de VoidAuthClient ou None en cas d'erreur.
    """
    global _voidauth_client
    
    # Si le client est déjà initialisé, on le retourne
    if _voidauth_client is not None:
        return _voidauth_client
    
    try:
        # Récupération de la configuration
        config = get_voidauth_config()
        
        # Création du client
        _voidauth_client = VoidAuthClient(
            server_url=config.server_url,
            realm=config.realm,
            client_id=config.client_id,
            client_secret=config.client_secret,
            admin_user=config.admin_user,
            admin_password=config.admin_password,
            verify_ssl=config.verify_ssl
        )
        
        logger.info("Client VoidAuth initialisé avec succès")
        return _voidauth_client
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du client VoidAuth: {str(e)}")
        return None

def reset_voidauth_client():
    """
    Réinitialise l'instance du client VoidAuth.
    
    Utile pour les tests ou pour forcer une réinitialisation.
    """
    global _voidauth_client
    _voidauth_client = None
    logger.info("Client VoidAuth réinitialisé")
