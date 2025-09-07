"""
Schémas Pydantic pour la gestion des recherches.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class SearchFilters(BaseModel):
    """Filtres avancés pour la recherche d'audiobooks."""
    genres: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    narrators: Optional[List[str]] = None
    language: Optional[str] = None
    min_duration: Optional[int] = None  # Durée minimale en secondes
    max_duration: Optional[int] = None  # Durée maximale en secondes
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    publish_year_from: Optional[int] = None
    publish_year_to: Optional[int] = None
    explicit: Optional[bool] = None
    abridged: Optional[bool] = None
    instances: Optional[List[str]] = None  # Liste d'IDs d'instances
    quality_min: Optional[int] = None  # Qualité minimale (bitrate)


class SearchQuery(BaseModel):
    """Requête de recherche."""
    q: str = Field(..., min_length=1, max_length=500, description="Terme de recherche")
    filters: Optional[SearchFilters] = None
    sort_by: Optional[str] = Field("relevance", regex="^(relevance|title|author|duration|rating|date)$")
    sort_order: Optional[str] = Field("desc", regex="^(asc|desc)$")
    page: Optional[int] = Field(1, ge=1)
    limit: Optional[int] = Field(20, ge=1, le=100)


class SearchHistoryBase(BaseModel):
    """Schéma de base pour l'historique des recherches."""
    query: str
    filters: Optional[str] = None
    results_count: int = 0
    execution_time_ms: int = 0
    is_suggestion: bool = False
    source: str = "manual"


class SearchHistoryCreate(SearchHistoryBase):
    """Schéma pour créer une entrée d'historique."""
    pass


class SearchHistory(SearchHistoryBase):
    """Schéma complet pour l'historique des recherches."""
    id: int
    user_id: int
    created_at: datetime
    last_used_at: datetime

    class Config:
        from_attributes = True


class SearchSuggestionBase(BaseModel):
    """Schéma de base pour les suggestions de recherche."""
    suggestion: str
    category: Optional[str] = None


class SearchSuggestion(SearchSuggestionBase):
    """Schéma complet pour les suggestions."""
    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """Résultat individuel de recherche."""
    audiobook_id: int
    title: str
    authors: List[str]
    narrators: List[str]
    duration: int
    language: str
    genres: List[str]
    rating: float
    publish_year: Optional[int]
    instance_name: str
    instance_id: int
    cover_path: Optional[str]
    score: float = 0.0  # Score de pertinence


class SearchResults(BaseModel):
    """Résultats de recherche complets."""
    query: str
    total_count: int
    results: List[SearchResult]
    suggestions: List[str] = []
    corrections: List[str] = []  # Corrections automatiques
    page: int
    limit: int
    has_more: bool
    execution_time_ms: int
    instances_searched: List[str]  # Noms des instances recherchées


class AutoCompleteRequest(BaseModel):
    """Requête pour l'auto-complétion."""
    query: str = Field(..., min_length=1, max_length=100)
    limit: Optional[int] = Field(10, ge=1, le=50)


class AutoCompleteResponse(BaseModel):
    """Réponse pour l'auto-complétion."""
    query: str
    suggestions: List[Dict[str, Any]]
    total_count: int