"""
Routes API pour la recherche avancée d'audiobooks.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.db.models import User
from app.schemas.search import (
    SearchQuery, SearchResults, SearchHistory, AutoCompleteRequest, AutoCompleteResponse
)
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/search", response_model=SearchResults)
async def search_audiobooks(
    query: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Effectue une recherche avancée d'audiobooks.

    - **q**: Terme de recherche (requis)
    - **filters**: Filtres avancés optionnels
    - **sort_by**: Tri par (relevance, title, author, duration, rating, date)
    - **sort_order**: Ordre de tri (asc, desc)
    - **page**: Numéro de page (défaut: 1)
    - **limit**: Nombre d'éléments par page (défaut: 20, max: 100)
    """
    try:
        search_service = SearchService(db)
        results = search_service.search_audiobooks(query, current_user.id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")


@router.get("/search/history", response_model=List[SearchHistory])
async def get_search_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des recherches récentes de l'utilisateur.

    - **limit**: Nombre maximum d'éléments à retourner (défaut: 20)
    """
    try:
        search_service = SearchService(db)
        history = search_service.get_search_history(current_user.id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique: {str(e)}")


@router.delete("/search/history/{history_id}")
async def delete_search_history_entry(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime une entrée spécifique de l'historique de recherche.

    - **history_id**: ID de l'entrée d'historique à supprimer
    """
    try:
        # Vérification que l'entrée appartient à l'utilisateur
        from app.db.models import SearchHistory as SearchHistoryModel
        entry = db.query(SearchHistoryModel).filter(
            SearchHistoryModel.id == history_id,
            SearchHistoryModel.user_id == current_user.id
        ).first()

        if not entry:
            raise HTTPException(status_code=404, detail="Entrée d'historique non trouvée")

        db.delete(entry)
        db.commit()

        return {"message": "Entrée d'historique supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.delete("/search/history")
async def clear_search_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime tout l'historique de recherche de l'utilisateur.
    """
    try:
        from app.db.models import SearchHistory as SearchHistoryModel
        db.query(SearchHistoryModel).filter(
            SearchHistoryModel.user_id == current_user.id
        ).delete()
        db.commit()

        return {"message": "Historique de recherche supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.post("/search/autocomplete", response_model=AutoCompleteResponse)
async def get_autocomplete_suggestions(
    request: AutoCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère des suggestions d'auto-complétion.

    - **query**: Terme partiellement saisi
    - **limit**: Nombre maximum de suggestions (défaut: 10)
    """
    try:
        search_service = SearchService(db)
        suggestions = search_service.get_autocomplete_suggestions(request.query, request.limit)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'auto-complétion: {str(e)}")


@router.get("/search/suggestions/popular")
async def get_popular_suggestions(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les suggestions de recherche populaires.

    - **limit**: Nombre maximum de suggestions (défaut: 10)
    """
    try:
        from app.db.models import SearchSuggestion
        suggestions = db.query(SearchSuggestion)\
            .order_by(SearchSuggestion.usage_count.desc(), SearchSuggestion.last_used_at.desc())\
            .limit(limit)\
            .all()

        return [
            {
                "suggestion": s.suggestion,
                "category": s.category,
                "usage_count": s.usage_count
            }
            for s in suggestions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des suggestions: {str(e)}")


@router.get("/search/stats")
async def get_search_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère des statistiques de recherche pour l'utilisateur.
    """
    try:
        from app.db.models import SearchHistory as SearchHistoryModel
        from sqlalchemy import func

        # Nombre total de recherches
        total_searches = db.query(func.count(SearchHistoryModel.id))\
            .filter(SearchHistoryModel.user_id == current_user.id)\
            .scalar()

        # Temps moyen d'exécution
        avg_execution_time = db.query(func.avg(SearchHistoryModel.execution_time_ms))\
            .filter(SearchHistoryModel.user_id == current_user.id)\
            .scalar()

        # Requêtes les plus fréquentes (top 5)
        top_queries = db.query(
            SearchHistoryModel.query,
            func.count(SearchHistoryModel.id).label('count')
        )\
        .filter(SearchHistoryModel.user_id == current_user.id)\
        .group_by(SearchHistoryModel.query)\
        .order_by(func.count(SearchHistoryModel.id).desc())\
        .limit(5)\
        .all()

        return {
            "total_searches": total_searches or 0,
            "average_execution_time_ms": float(avg_execution_time) if avg_execution_time else 0,
            "top_queries": [
                {"query": q.query, "count": q.count}
                for q in top_queries
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")