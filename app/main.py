#!/usr/bin/env python3
"""
Point d'entrée principal de l'application de gestion d'audiobooks.
"""
import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db import init_database, get_db, get_async_db
from app.core.api import api_router

# Configuration du cycle de vie de l'application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application FastAPI.
    
    Ce gestionnaire est responsable de l'initialisation et du nettoyage des ressources
    au démarrage et à l'arrêt de l'application.
    """
    # Démarrage de l'application
    logger = logging.getLogger(__name__)
    logger.info("Démarrage de l'application...")
    
    try:
        # Initialisation de la base de données (sauf en environnement de test)
        if not os.getenv("TESTING"):
            logger.info("Initialisation de la base de données...")
            init_database()
            logger.info("Base de données initialisée avec succès")
        else:
            logger.info("Mode test - Initialisation de la base de données différée")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise
    
    try:
        yield
    finally:
        # Nettoyage à l'arrêt
        if not os.getenv("TESTING"):
            logger.info("Arrêt de l'application...")

# Création de l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API pour la gestion de bibliothèques d'audiobooks",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Middleware pour le logging des requêtes
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log de la requête entrante
        print(f"Requête reçue: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            print(f"Erreur lors du traitement de la requête: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Erreur interne du serveur"}
            )

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajout du middleware de logging
app.add_middleware(LoggingMiddleware)

# Montage des dossiers statiques
app.mount(
    "/static",
    StaticFiles(directory=settings.STATIC_FOLDER),
    name="static"
)

# Import du schéma d'authentification depuis core.deps
from app.core.deps import oauth2_scheme

# Inclusion des routeurs API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Route racine
@app.get("/", tags=["Root"])
async def root():
    """
    Route racine de l'API.
    Retourne un message de bienvenue et des informations sur l'API.
    """
    return {
        "message": f"Bienvenue sur {settings.PROJECT_NAME}",
        "version": "0.2.0",
        "docs": "/docs",
        "api_version": settings.API_V1_STR
    }

# Route de santé
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Vérifie l'état de santé de l'application.
    Vérifie également la connexion à la base de données.
    """
    from sqlalchemy import text
    from app.db.session_manager import get_async_db_session
    
    try:
        async with get_async_db_session() as db:
            # Vérification de la connexion à la base de données
            await db.execute(text("SELECT 1"))
            return {
                "status": "ok",
                "database": "connected"
            }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }, 500

# Gestion des erreurs
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ressource non trouvée"}
    )

@app.exception_handler(500)
async def server_error_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

# Point d'entrée pour l'exécution en production
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
