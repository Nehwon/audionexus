"""
Package principal de l'application de gestion d'audiobooks.
"""
from .config import settings
from .database import init_db

# Initialisation de la base de données au démarrage
init_db()

__version__ = "0.2.0"
