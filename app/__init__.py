"""
Package principal de l'application de gestion d'audiobooks.
"""
import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_socketio import SocketIO
from config import Config
from app.db import db
from app.services import email as email_service

# Initialisation des extensions
migrate = Migrate()
jwt = JWTManager()
api = Api(version='1.0', title='AudioNexus API',
          description='API pour la gestion des livres audio')
socketio = SocketIO()

# Import différé pour éviter les imports circulaires
models = None
crud = None

__version__ = "0.4.0"  # Version mise à jour pour la refonte Flask

def create_app(config_class=Config):
    """Application factory pour créer une instance de l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configuration CORS
    CORS(app, resources={r"/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    
    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    api.init_app(app)
    
    # Configuration de Socket.IO
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get('SOCKETIO_CORS_ORIGINS', '*'),
        async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading'),
        logger=app.debug,
        engineio_logger=app.debug
    )
    
    # Import différé pour éviter les imports circulaires
    global models, crud
    from .db import models as models_module
    from . import crud as crud_module
    
    # Assignation des modules
    models = models_module
    crud = crud_module
    
    # Configuration de la base de données pour les tests
    if app.config.get('TESTING', False):
        with app.app_context():
            db.create_all()
    
    # Configuration du logging pour le service d'email
    email_logger = logging.getLogger('app.services.email')
    email_logger.setLevel(logging.INFO)
    
    # Si on est en mode debug, on active les logs détaillés
    if app.debug:
        email_logger.setLevel(logging.DEBUG)
    
    # Configuration du service d'email
    if app.config.get('MAIL_ENABLED', False):
        app.logger.info("Service d'emails activé")
    else:
        app.logger.warning("Service d'emails désactivé (MAIL_ENABLED=False)")
    
    # Initialisation de la base de données personnalisée
    from .db import init_db
    init_db(app)
    
    # Enregistrement des routes API
    from .core.api import auth as auth_routes
    from .core.api.audiobookshelf_router import router as audiobookshelf_router
    
    # Enregistrement des namespaces
    from .core.api import api as core_api
    core_api.add_namespace(auth_routes.api, path='/auth')
    core_api.add_namespace(audiobookshelf_router, path='/audiobookshelf')
    
    return app

# Pour permettre l'importation directe depuis app
__all__ = ['create_app', 'db', 'jwt', 'api', 'socketio', 'models', 'crud']
