"""
Routes FastAPI pour accéder aux données Audiobookshelf synchronisées localement.
Ces routes offrent une recherche et filtrage rapides sur les données locales.
"""
import logging
from typing import List, Optional, Dict, Any, Set

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.db import get_db
from app.db.models.audiobook import Audiobook, AudiobookProgress
from app.schemas.audiobook import AudiobookResponse, AudiobookSummary
from app.crud import audiobook as audiobook_crud
from app.db.models.base import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audiobookshelf/local", tags=["audiobookshelf-local"])


@router.get("/books", response_model=List[AudiobookSummary])
async def get_audiobooks(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum d'éléments à retourner"),
    search: Optional[str] = Query(None, description="Recherche dans titre, auteurs, description"),
    author: Optional[str] = Query(None, description="Filtrer par auteur"),
    genre: Optional[str] = Query(None, description="Filtrer par genre"),
    series: Optional[str] = Query(None, description="Filtrer par série"),
    language: Optional[str] = Query(None, description="Filtrer par langue (ex: fr, en)"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Note minimum (0-5)"),
    max_rating: Optional[float] = Query(None, ge=0, le=5, description="Note maximum (0-5)"),
    library_id: Optional[str] = Query(None, description="Filtrer par ID de bibliothèque source"),
    is_finished: Optional[bool] = Query(None, description="Filtrer par statut de lecture"),
    explicit_only: Optional[bool] = Query(None, description="Afficher uniquement les livres explicites"),
    sort_by: str = Query("title", description="Critère de tri (title, created_at, updated_at, rating, duration)"),
    sort_desc: bool = Query(False, description="Tri décroissant"),
    current_user: User = Depends(get_db)  # Placeholder for auth
):
    """
    Liste les livres audio synchronisés localement avec filtres avancés.

    Args:
        db: Session de base de données
        skip: Pagination - nombre d'éléments à ignorer
        limit: Pagination - nombre maximum d'éléments
        search: Recherche texte dans titre/auteurs/description
        author: Filtrer par auteur
        genre: Filtrer par genre
        series: Filtrer par série
        language: Filtrer par langue
        min_rating: Note minimum
        max_rating: Note maximum
        library_id: Filtrer par bibliothèque source
        is_finished: Filtrer par statut de lecture
        explicit_only: Afficher uniquement les livres explicites
        sort_by: Critère de tri
        sort_desc: Tri décroissant

    Returns:
        List[AudiobookSummary]: Liste des livres filtrés et triés
    """
    try:
        # Utiliser la fonction de recherche avancée du CRUD
        audiobooks = audiobook_crud.get_multi(
            db,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_desc=sort_desc,
            filters={
                'search': search,
                'author': author,
                'genre': genre,
                'series': series,
                'language': language,
                'min_rating': min_rating,
                'max_rating': max_rating,
                'library_id': library_id,
                'is_finished': is_finished,
                'explicit_only': explicit_only
            }
        )

        return audiobooks

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des livres audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des livres audio"
        )


@router.get("/books/{audiobook_id}", response_model=AudiobookResponse)
async def get_audiobook_by_id(
    audiobook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)  # Placeholder for auth
):
    """
    Récupère les détails d'un livre audio spécifique.

    Args:
        audiobook_id: ID du livre audio
        db: Session de base de données

    Returns:
        AudiobookResponse: Détails complets du livre
    """
    audiobook = audiobook_crud.get(db, id=audiobook_id)
    if not audiobook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livre audio {audiobook_id} non trouvé"
        )

    return audiobook


@router.get("/books/{audiobook_id}/progress", response_model=Dict[str, Any])
async def get_audiobook_progress(
    audiobook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)  # Placeholder for auth
):
    """
    Récupère la progression de lecture pour un livre audio.

    Args:
        audiobook_id: ID du livre audio
        db: Session de base de données

    Returns:
        Dict: Progression de lecture (placeholder pour l'instant)
    """
    # Pour une vraie implémentation, on récupérerait la progression de l'utilisateur actuel
    # Pour l'instant, on retourne la progression du livre (si disponible)
    audiobook = audiobook_crud.get(db, id=audiobook_id)
    if not audiobook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livre audio {audiobook_id} non trouvé"
        )

    # Placeholder - en réalité, on utiliserait le vrai système de progression
    return {
        "audiobook_id": audiobook_id,
        "progress": 0.0,
        "current_time": 0,
        "is_finished": False,
        "last_played": None
    }


@router.get("/stats", response_model=Dict[str, Any])
async def get_audiobooks_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)  # Placeholder for auth
):
    """
    Récupère les statistiques de la bibliothèque locale.

    Returns:
        Dict: Statistiques des livres audio
    """
    try:
        total_count = db.query(func.count(Audiobook.id)).scalar() or 0

        # Statistiques par genre
        genre_stats = db.query(
            func.json_extract(Audiobook.genres, '$[0]'),
            func.count(Audiobook.id)
        ).group_by(func.json_extract(Audiobook.genres, '$[0]')).all()

        # Statistiques par auteur
        author_stats = db.query(
            func.json_extract(Audiobook.authors, '$[0]'),
            func.count(Audiobook.id)
        ).group_by(func.json_extract(Audiobook.authors, '$[0]')).all()

        # Statistiques par langue
        language_stats = db.query(
            Audiobook.language,
            func.count(Audiobook.id)
        ).group_by(Audiobook.language).all()

        # Durée totale
        total_duration = db.query(func.sum(Audiobook.duration)).scalar() or 0

        return {
            "total_books": total_count,
            "total_duration_seconds": total_duration,
            "total_duration_hours": round(total_duration / 3600, 1) if total_duration else 0,
            "genres": {genre or "Non classé": count for genre, count in genre_stats},
            "authors": {author or "Auteur inconnu": count for author, count in author_stats},
            "languages": {lang or "Langue inconnue": count for lang, count in language_stats}
        }

    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du calcul des statistiques"
        )


@router.get("/genres", response_model=List[str])
async def get_genres(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)  # Placeholder for auth
):
    """
    Récupère la liste de tous les genres disponibles.

    Returns:
        List[str]: Liste des genres uniques
    """
    try:
        # Cette requête peut être optimisée selon le système de bases de données
        result = db.query(Audiobook.genres).filter(Audiobook.genres.isnot(None)).all()

        unique_genres: Set[str] = set()
        for genre_list in result:
            if genre_list[0]:  # genres est une liste JSON
                unique_genres.update(genre_list[0])

        return sorted(list(unique_genres))

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des genres: {str(e)}")
        return []


@router.get("/authors", response_model=List[str])
async def get_authors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)  # Placeholder for auth
):
    """
    Récupère la liste de tous les auteurs disponibles.

    Returns:
        List[str]: Liste des auteurs uniques
    """
    try:
        result = db.query(Audiobook.authors).filter(Audiobook.authors.isnot(None)).all()

        unique_authors: Set[str] = set()
        for author_list in result:
            if author_list[0]:  # authors est une liste JSON
                unique_authors.update(author_list[0])

        return sorted(list(unique_authors))

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des auteurs: {str(e)}")
        return []


@router.get("/series", response_model=List[str])
async def get_series(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)  # Placeholder for auth
):
    """
    Récupère la liste de toutes les séries disponibles.

    Returns:
        List[str]: Liste des séries uniques
    """
    try:
        result = db.query(Audiobook.series).filter(Audiobook.series.isnot(None)).all()

        unique_series: Set[str] = set()
        for series_list in result:
            if series_list[0]:  # series est une liste JSON
                for series in series_list[0]:
                    if isinstance(series, dict) and 'name' in series:
                        unique_series.add(series['name'])

        return sorted(list(unique_series))

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des séries: {str(e)}")
        return []