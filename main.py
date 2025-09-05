"""
Main FastAPI application for AudioNexus.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging

# Import the API router and app factory
from app.core.api import api_router
from app.config import Config

# Create FastAPI application
app = FastAPI(
    title="AudioNexus API",
    description="API pour la gestion des livres audio",
    version="0.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware sécurité
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Import des routes API
app.include_router(api_router, prefix="/api")

# Configuration du logging
logging.basicConfig(level=logging.INFO)

# Middleware de logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"HTTP {response.status_code}")
    return response

@app.get("/")
async def root():
    return {"message": "AudioNexus API", "version": "0.4.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )