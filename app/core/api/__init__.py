"""
Package contenant les routeurs et la logique d'API pour l'application.
"""
from fastapi import APIRouter

# Création du routeur principal FastAPI
api_router = APIRouter()

# Import des routeurs et inclusion dans le routeur principal
from .auth_router import router as auth_router
from .audiobookshelf_router import router as audiobookshelf_router
from .audiobookshelf_instances_router import router as audiobookshelf_instances_router
from .audiobookshelf_sync_router import router as audiobookshelf_sync_router
from .audiobookshelf_local_router import router as audiobookshelf_local_router

# Inclusion des routeurs dans le routeur principal
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(audiobookshelf_router, prefix="/audiobookshelf", tags=["audiobookshelf"])
api_router.include_router(audiobookshelf_instances_router, prefix="", tags=["audiobookshelf-instances"])
api_router.include_router(audiobookshelf_sync_router, prefix="", tags=["audiobookshelf-sync"])
api_router.include_router(audiobookshelf_local_router, prefix="", tags=["audiobookshelf-local"])
