from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.auth.router import router as auth_router
from app.api import api_router

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

# Inclure le routeur principal d'API
app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
)

# Événement de démarrage de l'application
@app.on_event("startup")
async def startup_event():
    # Initialiser la base de données
    init_db()
    print(f"{settings.PROJECT_NAME} v{settings.VERSION} démarré avec succès!")

# Montage des fichiers statiques (pour les fichiers téléchargés)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
