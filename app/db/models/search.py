"""
Modèles SQLAlchemy pour la gestion des recherches et de leur historique.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.db.database import Base


class SearchHistory(Base):
    """Historique des recherches effectuées par les utilisateurs."""
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)

    # Relation avec l'utilisateur
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Contenu de la recherche
    query = Column(String(500), nullable=False, index=True)  # Terme de recherche principal
    filters = Column(Text, nullable=True)  # Filtres JSON serialisés

    # Résultats et métriques
    results_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)  # Temps d'exécution

    # Métadonnées
    is_suggestion = Column(Boolean, default=False)  # Recherche issue d'une suggestion
    source = Column(String(50), default="manual")  # manual, suggestion, auto_complete

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Index pour les performances
    __table_args__ = (
        Index('ix_search_history_user_query', 'user_id', 'query'),
        Index('ix_search_history_created_at', 'created_at'),
        Index('ix_search_history_last_used', 'last_used_at'),
    )

    def __repr__(self):
        return f"<SearchHistory {self.id}: '{self.query}' by user {self.user_id}>"


class SearchSuggestion(Base):
    """Suggestions de recherche populaires."""
    __tablename__ = "search_suggestions"

    id = Column(Integer, primary_key=True, index=True)

    # Contenu de la suggestion
    suggestion = Column(String(255), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=True)  # auteur, titre, genre, etc.

    # Métriques de popularité
    usage_count = Column(Integer, default=1)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Index pour les performances
    __table_args__ = (
        Index('ix_search_suggestions_usage', 'usage_count', 'last_used_at'),
        Index('ix_search_suggestions_category', 'category'),
    )

    def __repr__(self):
        return f"<SearchSuggestion '{self.suggestion}': {self.usage_count} uses>"


# Mise à jour du fichier __init__.py pour importer les nouveaux modèles
__all__ = ["SearchHistory", "SearchSuggestion"]