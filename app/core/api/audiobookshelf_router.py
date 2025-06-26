"""
Routeurs pour l'intégration avec Audiobookshelf.
"""
import json
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse

from app.core.dependencies import get_audiobookshelf_client, get_current_user
from app.core.api.audiobookshelf import AudiobookshelfClient
from app.db.models.base import User
from app.config import settings
import os
import tempfile

router = APIRouter()

# Fonctions utilitaires
def _handle_abs_error(e: Exception, operation: str) -> None:
    """Gère les erreurs de l'API Audiobookshelf."""
    error_msg = str(e)
    if "404" in error_msg or "not found" in error_msg.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ressource non trouvée: {error_msg}"
        )
    elif "401" in error_msg or "unauthorized" in error_msg.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Non autorisé: {error_msg}"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de {operation}: {error_msg}"
        )

# Routes des bibliothèques
@router.get("/libraries", response_model=List[Dict[str, Any]])
async def get_libraries(
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des bibliothèques Audiobookshelf.
    
    Returns:
        List[Dict]: Liste des bibliothèques disponibles avec leurs métadonnées
    """
    try:
        return client.get_libraries()
    except Exception as e:
        _handle_abs_error(e, "la récupération des bibliothèques")

@router.get("/libraries/{library_id}", response_model=Dict[str, Any])
async def get_library(
    library_id: str,
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les détails d'une bibliothèque spécifique.
    
    Args:
        library_id: ID de la bibliothèque à récupérer
        
    Returns:
        Dict: Détails de la bibliothèque
    """
    try:
        return client.get_library(library_id)
    except Exception as e:
        _handle_abs_error(e, f"la récupération de la bibliothèque {library_id}")

# Routes des livres audio
@router.get("/recently-added", response_model=List[Dict[str, Any]])
async def get_recently_added(
    limit: int = Query(10, ge=1, le=100, description="Nombre maximum de livres à retourner"),
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les livres audio récemment ajoutés.
    
    Args:
        limit: Nombre maximum de livres à retourner (1-100, défaut: 10)
        
    Returns:
        List[Dict]: Liste des livres récemment ajoutés
    """
    try:
        return client.get_recently_added(limit=limit)
    except Exception as e:
        _handle_abs_error(e, "la récupération des livres récents")

@router.get("/items/{item_id}", response_model=Dict[str, Any])
async def get_audiobook(
    item_id: str,
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les détails d'un livre audio spécifique.
    
    Args:
        item_id: ID du livre audio à récupérer
        
    Returns:
        Dict: Détails du livre audio
    """
    try:
        return client.get_audiobook(item_id)
    except Exception as e:
        _handle_abs_error(e, f"la récupération du livre audio {item_id}")

# Routes de recherche
@router.get("/search", response_model=List[Dict[str, Any]])
async def search_audiobooks(
    query: str = Query(..., min_length=1, description="Terme de recherche"),
    library_id: Optional[str] = Query(None, description="Filtrer par ID de bibliothèque"),
    limit: int = Query(10, ge=1, le=50, description="Nombre maximum de résultats"),
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Recherche des livres audio.
    
    Args:
        query: Terme de recherche
        library_id: ID de la bibliothèque pour filtrer les résultats (optionnel)
        limit: Nombre maximum de résultats (1-50, défaut: 10)
        
    Returns:
        List[Dict]: Résultats de la recherche
    """
    try:
        if library_id:
            return client.search_library(library_id, query)[:limit]
        
        # Si pas de bibliothèque spécifiée, chercher dans toutes les bibliothèques
        all_results = []
        libraries = client.get_libraries()
        
        for lib in libraries:
            try:
                results = client.search_library(lib['id'], query)
                all_results.extend(results)
            except Exception:
                continue
                
        return all_results[:limit]
    except Exception as e:
        _handle_abs_error(e, f"la recherche de '{query}'")

# Routes des collections
@router.get("/collections", response_model=List[Dict[str, Any]])
async def get_collections(
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des collections.
    
    Returns:
        List[Dict]: Liste des collections
    """
    try:
        return client.get_collections()
    except Exception as e:
        _handle_abs_error(e, "la récupération des collections")

# Routes de progression de lecture
@router.get("/progress/{user_id}/{item_id}", response_model=Dict[str, Any])
async def get_reading_progress(
    user_id: str,
    item_id: str,
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la progression de lecture d'un utilisateur pour un livre audio.
    
    Args:
        user_id: ID de l'utilisateur
        item_id: ID du livre audio
        
    Returns:
        Dict: Progression de lecture
    """
    try:
        return client.get_progress(user_id, item_id)
    except Exception as e:
        _handle_abs_error(e, f"la récupération de la progression pour l'utilisateur {user_id}, livre {item_id}")

@router.post("/progress/{user_id}/{item_id}", response_model=Dict[str, Any])
async def update_reading_progress(
    user_id: str,
    item_id: str,
    progress: float = Form(..., ge=0, le=1, description="Progression (0-1)"),
    current_time: float = Form(..., ge=0, description="Temps actuel en secondes"),
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour la progression de lecture d'un utilisateur pour un livre audio.
    
    Args:
        user_id: ID de l'utilisateur
        item_id: ID du livre audio
        progress: Progression (0-1)
        current_time: Temps actuel en secondes
        
    Returns:
        Dict: Confirmation de la mise à jour
    """
    try:
        return client.update_progress(user_id, item_id, progress, current_time)
    except Exception as e:
        _handle_abs_error(e, f"la mise à jour de la progression pour l'utilisateur {user_id}, livre {item_id}")

# Routes d'administration (nécessitent les droits admin)
@router.get("/admin/users", response_model=List[Dict[str, Any]])
async def get_users(
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des utilisateurs (admin uniquement).
    
    Returns:
        List[Dict]: Liste des utilisateurs
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé: droits administrateur requis"
            )
        return client.get_users()
    except HTTPException:
        raise
    except Exception as e:
        _handle_abs_error(e, "la récupération de la liste des utilisateurs")

# Routes de téléversement de fichiers
@router.post("/upload", response_model=Dict[str, Any])
async def upload_audiobook(
    library_id: str = Form(...),
    file: UploadFile = File(...),
    metadata: str = Form("{}", description="Métadonnées au format JSON"),
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Téléverse un nouveau livre audio.
    
    Args:
        library_id: ID de la bibliothèque cible
        file: Fichier audio à téléverser
        metadata: Métadonnées au format JSON (optionnel)
        
    Returns:
        Dict: Résultat du téléversement
    """
    try:
        # Enregistrer le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Parser les métadonnées
        try:
            metadata_dict = json.loads(metadata) if metadata else {}
        except json.JSONDecodeError:
            metadata_dict = {}
        
        # Téléverser le fichier
        result = client.upload_audiobook(library_id, temp_path, metadata_dict)
        
        # Nettoyer le fichier temporaire
        try:
            os.unlink(temp_path)
        except:
            pass
            
        return result
        
    except Exception as e:
        # S'assurer de nettoyer le fichier temporaire en cas d'erreur
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        _handle_abs_error(e, "le téléversement du livre audio")
