"""
Package contenant les routeurs et la logique d'API pour l'application.
"""
from fastapi import APIRouter

# Création du routeur principal
api_router = APIRouter()

# Import des routeurs des différents modules
from . import auth

# Inclusion des routeurs
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
