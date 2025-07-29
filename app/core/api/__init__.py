"""
Package contenant les routeurs et la logique d'API pour l'application.
"""
from flask_restx import Api

# Création de l'API principale
api = Api(
    version='1.0',
    title='AudioNexus API',
    description='API pour la gestion des livres audio',
    doc='/docs',
    default='AudioNexus',
    default_label='Endpoints principaux',
    validate=True
)

# Import des namespaces API
from . import auth
from . import audiobookshelf_router
