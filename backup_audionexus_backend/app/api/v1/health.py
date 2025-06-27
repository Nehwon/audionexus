from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de santé utilisé par Docker et les outils de monitoring.
    Retourne un statut 200 si l'API est opérationnelle.
    """
    return {
        "status": "ok", 
        "service": settings.PROJECT_NAME, 
        "version": settings.VERSION
    }
