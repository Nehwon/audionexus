"""
Package principal de l'application de gestion d'audiobooks.
"""
from .config import settings

# Import différé pour éviter les imports circulaires
models = None
crud = None

__version__ = "0.3.6"  # Doit correspondre à la version dans pyproject.toml

def init_app():
    """Initialise l'application et ses dépendances."""
    global models, crud
    
    # Import différé pour éviter les imports circulaires
    from . import db
    from .db import models as models_module
    from . import crud as crud_module
    
    # Initialisation de la base de données
    db.init_database()
    
    # Assignation des modules
    models = models_module
    crud = crud_module
    
    return {
        'settings': settings,
        'models': models,
        'crud': crud,
        'db': db
    }

# Pour permettre l'importation directe depuis app
__all__ = ['settings', 'models', 'crud', 'init_app']
