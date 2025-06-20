"""
Package principal de l'application de gestion d'audiobooks.
"""
from .config import settings
from .db import models
from . import crud

__version__ = "0.2.0"

# Pour permettre l'importation directe depuis app
__all__ = ['settings', 'models', 'crud']
