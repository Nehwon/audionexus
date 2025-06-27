# Package pour les routes API

from fastapi import APIRouter

api_router = APIRouter()

# Inclure les routeurs d'API
from . import login, users, file_processing

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(file_processing.router, prefix="/file-processing", tags=["file-processing"])
