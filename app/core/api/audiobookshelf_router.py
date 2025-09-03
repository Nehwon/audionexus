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

# Routes de recherche avancées
@router.get("/search", response_model=List[Dict[str, Any]])
async def search_audiobooks(
    query: str = Query(..., min_length=1, description="Terme de recherche"),
    library_id: Optional[str] = Query(None, description="Filtrer par ID de bibliothèque"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de résultats"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination"),
    sort_by: str = Query("addedAt", description="Critère de tri (addedAt, title, author, duration)"),
    sort_desc: bool = Query(True, description="Tri décroissant"),
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Recherche avancée des livres audio avec pagination et tris.

    Args:
        query: Terme de recherche
        library_id: ID de la bibliothèque pour filtrer les résultats (optionnel)
        limit: Nombre maximum de résultats (1-100, défaut: 20)
        offset: Décalage pour la pagination
        sort_by: Critère de tri
        sort_desc: Tri décroissant

    Returns:
        List[Dict]: Résultats de la recherche
    """
    try:
        if library_id:
            results = client.search_library(library_id, query)
        else:
            # Chercher dans toutes les bibliothèques
            all_results = []
            libraries = client.get_libraries()

            for lib in libraries:
                try:
                    results = client.search_library(lib['id'], query)
                    all_results.extend(results)
                except Exception:
                    continue

            results = all_results

        # Appliquer la pagination et le tri
        # Note: Le tri réel devrait être fait côté Audiobookshelf si possible
        start_idx = offset
        end_idx = offset + limit

        return results[start_idx:end_idx]
    except Exception as e:
        _handle_abs_error(e, f"la recherche de '{query}'")


@router.get("/items/filter", response_model=List[Dict[str, Any]])
async def filter_audiobooks(
    author: Optional[str] = Query(None, description="Filtrer par auteur"),
    genre: Optional[str] = Query(None, description="Filtrer par genre"),
    series: Optional[str] = Query(None, description="Filtrer par série"),
    language: Optional[str] = Query(None, description="Filtrer par langue"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Note minimum (0-5)"),
    min_duration: Optional[int] = Query(None, ge=0, description="Durée minimum en secondes"),
    library_id: Optional[str] = Query(None, description="Filtrer par ID de bibliothèque"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de résultats"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination"),
    client: AudiobookshelfClient = Depends(get_audiobookshelf_client),
    current_user: User = Depends(get_current_user)
):
    """
    Filtre avancé des livres audio par métadonnées.

    Args:
        author: Filtrer par auteur
        genre: Filtrer par genre
        series: Filtrer par série
        language: Filtrer par langue
        min_rating: Note minimum
        min_duration: Durée minimum
        library_id: ID de la bibliothèque
        limit: Nombre maximum de résultats
        offset: Décalage pour la pagination

    Returns:
        List[Dict]: Livres filtrés
    """
    try:
        # Pour une vraie implémentation, on utiliserait l'API de filtrage d'Audiobookshelf
        # Pour l'instant, on utilise la recherche et on filtre côté serveur
        filtered_results = []

        if library_id:
            libraries = [client.get_library(library_id)]
        else:
            libraries = client.get_libraries()

        for lib in libraries:
            lib_id = lib.get('id')
            if not lib_id:
                continue

            # Récupérer tous les livres de la bibliothèque (limite pour la démonstration)
            try:
                items = client.search_library(lib_id, "")
                for item in items[:200]:  # Limite pour éviter les timeouts
                    metadata = item.get('metadata', {})

                    # Appliquer les filtres
                    if author and author.lower() not in ' '.join(metadata.get('author', [])).lower():
                        continue
                    if genre and not any(genre.lower() in g.lower() for g in metadata.get('genres', [])):
                        continue
                    if series and not any(series.lower() in s.get('name', '').lower() for s in metadata.get('series', [])):
                        continue
                    if language and language.lower() != metadata.get('language', '').lower():
                        continue
                    if min_rating and (metadata.get('rating', 0) or 0) < min_rating:
                        continue
                    if min_duration and (metadata.get('duration', 0) or 0) < min_duration:
                        continue

                    filtered_results.append(item)

            except Exception:
                continue

        # Pagination
        start_idx = offset
        end_idx = offset + limit

        return filtered_results[start_idx:end_idx]

    except Exception as e:
        _handle_abs_error(e, "le filtrage des livres audio")

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
