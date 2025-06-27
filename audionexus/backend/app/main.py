import logging
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, logger as db_logger
from app.api.v1.auth.router import router as auth_router

# Configuration du logger racine
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Création du logger pour ce module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Création de l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API pour la gestion des bibliothèques audio AudioNexus",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Gestion des erreurs globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Route racine
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Bienvenue sur l'API {settings.PROJECT_NAME} v{settings.VERSION}",
        "documentation": "/docs",
    }

# Inclure les routeurs
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"],
)

# Événement de démarrage de l'application
@app.on_event("startup")
async def startup_event():
    logger.info("\n" + "="*80)
    logger.info(f"DÉMARRAGE DE L'APPLICATION {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info("="*80 + "\n")
    
    # Afficher les variables d'environnement pour le débogage
    logger.info("Variables d'environnement:")
    logger.info(f"- DATABASE_URL: {settings.DATABASE_URL}")
    logger.info(f"- FIRST_SUPERUSER_EMAIL: {settings.FIRST_SUPERUSER_EMAIL}")
    logger.info(f"- FIRST_SUPERUSER_PASSWORD: {'*' * len(settings.FIRST_SUPERUSER_PASSWORD) if settings.FIRST_SUPERUSER_PASSWORD else 'Non défini'}\n")
    
    # Initialiser la base de données
    logger.info("Appel de init_db()...")
    try:
        init_db()
        logger.info("✓ init_db() terminé avec succès\n")
    except Exception as e:
        logger.error(f"✗ ERREUR lors de l'appel à init_db(): {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info(f"\n{settings.PROJECT_NAME} v{settings.VERSION} démarré avec succès!\n")

# Montage des fichiers statiques (pour les fichiers téléchargés)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
