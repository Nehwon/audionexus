"""
Package contenant les routeurs et la logique d'API pour l'application.
"""
from fastapi import APIRouter

# Création du routeur principal
api_router = APIRouter()

# Import des routeurs des différents modules
# from . import users, books, libraries, etc.

# Inclusion des routeurs
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(books.router, prefix="/books", tags=["books"])
# api_router.include_router(libraries.router, prefix="/libraries", tags=["libraries"])
