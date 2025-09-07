"""
Module d'intégration avec VoidAuth pour la gestion de l'authentification.

Ce module fournit une interface pour interagir avec le service VoidAuth (basé sur Keycloak)
pour la gestion des utilisateurs, des rôles et des permissions.
"""

import logging
from typing import Any, Dict, List, Optional

# Configuration du logger
logger = logging.getLogger(__name__)

# Import du client VoidAuth
try:
    from .client import VoidAuthClient
except ImportError as e:
    logger.warning(f"Impossible d'importer VoidAuthClient: {e}")

__all__ = ["VoidAuthClient"]
