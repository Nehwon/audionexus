"""
Package principal de l'application de gestion d'audiobooks.
"""

import logging

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from flask_socketio import SocketIO

from app.db import db

from .config import Config

# Initialisation des extensions
migrate = Migrate()
jwt = JWTManager()
api = Api(
    version="1.0",
    title="AudioNexus API",
    description="API pour la gestion des livres audio",
)
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
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Initialisation des extensions
    # db.init_app(app)  # Désactivé - utilisation d'architecture SQLAlchemy pure
    migrate.init_app(app, db)
    jwt.init_app(app)
    api.init_app(app)

    # Configuration de Socket.IO
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("SOCKETIO_CORS_ORIGINS", "*"),
        async_mode=app.config.get("SOCKETIO_ASYNC_MODE", "threading"),
        logger=app.debug,
        engineio_logger=app.debug,
    )

    # Import différé pour éviter les imports circulaires
    global models, crud
    from . import crud as crud_module
    from .db import models as models_module

    # Assignation des modules
    models = models_module
    crud = crud_module

    # Configuration de la base de données pour les tests
    if app.config.get("TESTING", False):
        with app.app_context():
            db.create_all()

    # Configuration du logging pour le service d'email
    email_logger = logging.getLogger("app.services.email")
    email_logger.setLevel(logging.INFO)

    # Si on est en mode debug, on active les logs détaillés
    if app.debug:
        email_logger.setLevel(logging.DEBUG)

    # Configuration du service d'email
    if app.config.get("MAIL_ENABLED", False):
        app.logger.info("Service d'emails activé")
    else:
        app.logger.warning("Service d'emails désactivé (MAIL_ENABLED=False)")

    # Initialisation de la base de données personnalisée
    from .db import init_db

    init_db()  # Pas d'argument app nécessaire pour l'architecture SQLAlchemy pure

    # Enregistrement des routes API (géré dans core.api.__init__)
    # Les routeurs FastAPI sont inclus dans app/core/api/__init__.py
    from fastapi import FastAPI

    # Intégration FastAPI avec Flask pour compatibilité
    from flask import request

    from app.core.api import api_router

    fastapi_app = FastAPI()
    fastapi_app.include_router(api_router, prefix="/api")

    # Monter FastAPI sur Flask via WSGI middleware
    @app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def api_routes(path):
        """Gestionnaire de routes pour les endpoints FastAPI dans Flask"""
        from fastapi.testclient import TestClient

        # Debug logging
        app.logger.info(f"FastAPI route called with path: {path}")

        test_client = TestClient(fastapi_app)
        try:
            response = test_client.request(
                request.method,
                f"/{path}",
                data=request.get_data(),
                headers={
                    k: v for k, v in request.headers.items() if k.lower() != "host"
                },
                cookies=request.cookies,
            )
            app.logger.info(f"FastAPI response: {response.status_code}")
            return app.response_class(
                response.content, response.status_code, response.headers
            )
        except Exception as e:
            app.logger.error(f"FastAPI error: {str(e)}")
            return app.response_class(b"Internal Server Error", 500)

    return app


# Pour permettre l'importation directe depuis app
__all__ = ["create_app", "db", "jwt", "api", "socketio", "models", "crud"]
