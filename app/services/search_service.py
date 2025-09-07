"""
Service de recherche avancée multi-collection pour audiobooks.
"""

import difflib
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, or_, text
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from app.db.models import (
    Audiobook,
    AudiobookshelfInstance,
    SearchHistory,
    SearchSuggestion,
)
from app.schemas.search import (
    AutoCompleteResponse,
    SearchFilters,
)
from app.schemas.search import SearchHistory as SearchHistorySchema
from app.schemas.search import (
    SearchQuery,
    SearchResult,
    SearchResults,
)


class SearchService:
    """Service principal pour les recherches d'audiobooks."""

    def __init__(self, db: Session):
        self.db = db

    def search_audiobooks(self, query: SearchQuery, user_id: int) -> SearchResults:
        """
        Effectue une recherche avancée d'audiobooks.

        Args:
            query: Les paramètres de recherche
            user_id: ID de l'utilisateur effectuant la recherche

        Returns:
            Résultats de recherche formatés
        """
        start_time = time.time()

        # Validation de la requête
        self._validate_search_query(query)

        # Construction de la requête de base
        sql_query = self._build_search_query(query)

        # Exécution de la recherche
        raw_results = self.db.execute(sql_query).fetchall()

        # Traitement des résultats
        results, total_count = self._process_search_results(raw_results, query)

        # Calcul du temps d'exécution
        execution_time = int((time.time() - start_time) * 1000)

        # Génération des suggestions
        suggestions = self._generate_suggestions(query.q)

        # Génération des corrections automatiques
        corrections = self._generate_corrections(query.q)

        # Liste des instances recherchées
        instances_searched = self._get_instances_searched(query.filters)

        # Enregistrement dans l'historique
        self._save_search_history(query, user_id, total_count, execution_time)

        return SearchResults(
            query=query.q,
            total_count=total_count,
            results=results,
            suggestions=suggestions,
            corrections=corrections,
            page=query.page,
            limit=query.limit,
            has_more=(query.page * query.limit) < total_count,
            execution_time_ms=execution_time,
            instances_searched=instances_searched,
        )

    def _validate_search_query(self, query: SearchQuery) -> None:
        """Valide les paramètres de recherche."""
        if len(query.q.strip()) < 1:
            raise ValueError("La requête de recherche ne peut pas être vide")

    def _build_search_query(self, query: SearchQuery) -> text:
        """
        Construit la requête SQL pour la recherche.

        Utilise les capacités full-text de PostgreSQL avec des poids pour améliorer la pertinence.
        """
        # Construction des conditions de recherche full-text
        search_conditions = []
        search_vector_parts = []

        # Recherche dans les champs principaux avec poids
        if query.q:
            # Titre (poids A - plus important)
            search_vector_parts.append(f"setweight(to_tsvector('french', title), 'A')")

            # Auteurs (poids B)
            search_vector_parts.append(
                "setweight(to_tsvector('french', array_to_string(authors, ' ')), 'B')"
            )

            # Narrateurs (poids C)
            search_vector_parts.append(
                "setweight(to_tsvector('french', array_to_string(narrators, ' ')), 'C')"
            )

            # Description (poids D)
            search_vector_parts.append(
                "setweight(to_tsvector('french', COALESCE(description, '')), 'D')"
            )

            # Recherche full-text combinée
            combined_vector = f"({' || '.join(search_vector_parts)})"
            search_query = func.plainto_tsquery("french", query.q)
            search_conditions.append(f"{combined_vector} @@ {search_query}")

        # Construction du SELECT avec calcul de score
        select_parts = [
            "a.id as audiobook_id",
            "a.title",
            "a.authors",
            "a.narrators",
            "a.duration",
            "a.language",
            "a.genres",
            "a.rating",
            "a.publish_year",
            "a.cover_path",
            "i.name as instance_name",
            "i.id as instance_id",
        ]

        # Ajout du score de pertinence si recherche textuelle
        if query.q:
            select_parts.append(f"ts_rank({combined_vector}, {search_query}) as score")
        else:
            select_parts.append("1.0 as score")

        # Construction du FROM avec JOIN
        from_clause = """
        FROM audiobooks a
        JOIN audiobookshelf_instances i ON a.library_id = i.id
        """

        # Conditions WHERE de base
        where_conditions = ["a.id IS NOT NULL"]

        # Ajout conditions de recherche textuelle
        if search_conditions:
            where_conditions.extend(search_conditions)

        # Ajout des filtres avancés
        filter_conditions = self._build_filter_conditions(query.filters)
        if filter_conditions:
            where_conditions.extend(filter_conditions)

        # Construction du ORDER BY
        order_by = self._build_order_by(query)

        # Pagination
        offset = (query.page - 1) * query.limit
        limit_clause = f"LIMIT {query.limit} OFFSET {offset}"

        # Construction de la requête finale
        sql = f"""
        SELECT {', '.join(select_parts)}
        {from_clause}
        WHERE {' AND '.join(where_conditions)}
        {order_by}
        {limit_clause}
        """

        return text(sql)

    def _build_filter_conditions(self, filters: Optional[SearchFilters]) -> List[str]:
        """Construit les conditions WHERE pour les filtres avancés."""
        conditions = []

        if not filters:
            return conditions

        if filters.genres:
            # Recherche dans le tableau des genres
            genre_conditions = []
            for genre in filters.genres:
                genre_conditions.append(f"'{genre}' = ANY(a.genres)")
            conditions.append(f"({' OR '.join(genre_conditions)})")

        if filters.authors:
            author_conditions = []
            for author in filters.authors:
                author_conditions.append(f"'{author}' = ANY(a.authors)")
            conditions.append(f"({' OR '.join(author_conditions)})")

        if filters.narrators:
            narrator_conditions = []
            for narrator in filters.narrators:
                narrator_conditions.append(f"'{narrator}' = ANY(a.narrators)")
            conditions.append(f"({' OR '.join(narrator_conditions)})")

        if filters.language:
            conditions.append(f"a.language = '{filters.language}'")

        if filters.min_duration:
            conditions.append(f"a.duration >= {filters.min_duration}")

        if filters.max_duration:
            conditions.append(f"a.duration <= {filters.max_duration}")

        if filters.min_rating:
            conditions.append(f"a.rating >= {filters.min_rating}")

        if filters.max_rating:
            conditions.append(f"a.rating <= {filters.max_rating}")

        if filters.publish_year_from:
            conditions.append(f"a.publish_year >= {filters.publish_year_from}")

        if filters.publish_year_to:
            conditions.append(f"a.publish_year <= {filters.publish_year_to}")

        if filters.explicit is not None:
            conditions.append(f"a.is_explicit = {filters.explicit}")

        if filters.abridged is not None:
            conditions.append(f"a.is_abridged = {filters.abridged}")

        if filters.instances:
            instance_conditions = []
            for instance_name in filters.instances:
                instance_conditions.append(f"i.name = '{instance_name}'")
            conditions.append(f"({' OR '.join(instance_conditions)})")

        if filters.quality_min:
            conditions.append(f"a.bitrate >= {filters.quality_min}")

        return conditions

    def _build_order_by(self, query: SearchQuery) -> str:
        """Construit la clause ORDER BY."""
        sort_column_map = {
            "relevance": "score",
            "title": "a.title",
            "author": "a.authors[1]",  # Premier auteur
            "duration": "a.duration",
            "rating": "a.rating",
            "date": "a.publish_year",
        }

        column = sort_column_map.get(query.sort_by, "score")
        direction = "DESC" if query.sort_order == "desc" else "ASC"

        if query.sort_by == "relevance" and not query.q:
            # Si pas de recherche textuelle, tri par titre
            return "ORDER BY a.title ASC"
        else:
            return f"ORDER BY {column} {direction}"

    def _process_search_results(
        self, raw_results: List, query: SearchQuery
    ) -> Tuple[List[SearchResult], int]:
        """Traite les résultats bruts de la recherche."""
        results = []

        for row in raw_results:
            result = SearchResult(
                audiobook_id=row.audiobook_id,
                title=row.title,
                authors=row.authors or [],
                narrators=row.narrators or [],
                duration=row.duration,
                language=row.language,
                genres=row.genres or [],
                rating=row.rating,
                publish_year=row.publish_year,
                instance_name=row.instance_name,
                instance_id=row.instance_id,
                cover_path=row.cover_path,
                score=getattr(row, "score", 0.0),
            )
            results.append(result)

        # Pour l'instant, on ne retourne que les résultats de la page
        # TODO: Implémenter un comptage total plus efficace
        total_count = (
            len(results) * query.page
            if len(results) == query.limit
            else (query.page - 1) * query.limit + len(results)
        )

        return results, total_count

    def _generate_suggestions(self, query: str) -> List[str]:
        """Génère des suggestions basées sur l'historique des recherches."""
        if len(query) < 2:
            return []

        # Recherche des termes similaires dans l'historique
        similar_queries = (
            self.db.query(SearchHistory.query)
            .filter(SearchHistory.query.ilike(f"%{query}%"))
            .distinct()
            .limit(5)
            .all()
        )

        suggestions = [q.query for q in similar_queries if q.query != query]

        # Recherche dans les suggestions populaires
        popular_suggestions = (
            self.db.query(SearchSuggestion.suggestion)
            .filter(SearchSuggestion.suggestion.ilike(f"%{query}%"))
            .order_by(SearchSuggestion.usage_count.desc())
            .limit(3)
            .all()
        )

        popular = [s.suggestion for s in popular_suggestions]

        # Combinaison des suggestions
        all_suggestions = suggestions + popular
        return list(set(all_suggestions))[:5]

    def _generate_corrections(self, query: str) -> List[str]:
        """Génère des corrections automatiques pour les termes mal orthographiés."""
        words = query.split()
        corrections = []

        for word in words:
            if len(word) < 4:  # Pas de correction pour les mots courts
                continue

            # Recherche de termes similaires dans les titres et auteurs
            similar_titles = (
                self.db.query(Audiobook.title)
                .filter(Audiobook.title.ilike(f"%{word}%"))
                .distinct()
                .limit(3)
                .all()
            )

            similar_authors = (
                self.db.query(func.unnest(Audiobook.authors))
                .filter(func.unnest(Audiobook.authors).ilike(f"%{word}%"))
                .distinct()
                .limit(3)
                .all()
            )

            candidates = [t.title for t in similar_titles] + [
                a[0] for a in similar_authors
            ]
            candidates = list(set(candidates))

            if candidates:
                # Prendre le candidat le plus proche
                closest = difflib.get_close_matches(word, candidates, n=1)
                if closest:
                    corrections.append(closest[0])

        return corrections[:3]

    def _get_instances_searched(self, filters: Optional[SearchFilters]) -> List[str]:
        """Retourne la liste des instances recherchées."""
        query = self.db.query(AudiobookshelfInstance.name)

        if filters and filters.instances:
            query = query.filter(AudiobookshelfInstance.name.in_(filters.instances))
        else:
            query = query.filter(AudiobookshelfInstance.is_active == True)

        instances = query.all()
        return [i.name for i in instances]

    def _save_search_history(
        self, query: SearchQuery, user_id: int, results_count: int, execution_time: int
    ) -> None:
        """Enregistre la recherche dans l'historique."""
        filters_json = json.dumps(query.filters.dict() if query.filters else {})

        history_entry = SearchHistory(
            user_id=user_id,
            query=query.q,
            filters=filters_json,
            results_count=results_count,
            execution_time_ms=execution_time,
        )

        self.db.add(history_entry)
        self.db.commit()

    def get_search_history(
        self, user_id: int, limit: int = 20
    ) -> List[SearchHistorySchema]:
        """Récupère l'historique des recherches d'un utilisateur."""
        history_entries = (
            self.db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.last_used_at.desc())
            .limit(limit)
            .all()
        )

        return [SearchHistorySchema.from_orm(entry) for entry in history_entries]

    def get_autocomplete_suggestions(
        self, query: str, limit: int = 10
    ) -> AutoCompleteResponse:
        """Génère des suggestions d'auto-complétion."""
        if len(query) < 2:
            return AutoCompleteResponse(query=query, suggestions=[], total_count=0)

        # Recherche dans les titres
        title_suggestions = (
            self.db.query(
                Audiobook.title.label("suggestion"),
                func.count(Audiobook.id).label("count"),
                func.literal("title").label("type"),
            )
            .filter(Audiobook.title.ilike(f"{query}%"))
            .group_by(Audiobook.title)
            .order_by(func.count(Audiobook.id).desc())
            .limit(limit // 3)
            .all()
        )

        # Recherche dans les auteurs
        author_suggestions = (
            self.db.query(
                func.unnest(Audiobook.authors).label("suggestion"),
                func.count(func.unnest(Audiobook.authors)).label("count"),
                func.literal("author").label("type"),
            )
            .filter(func.unnest(Audiobook.authors).ilike(f"{query}%"))
            .group_by(func.unnest(Audiobook.authors))
            .order_by(func.count(func.unnest(Audiobook.authors)).desc())
            .limit(limit // 3)
            .all()
        )

        # Recherche dans les genres
        genre_suggestions = (
            self.db.query(
                func.unnest(Audiobook.genres).label("suggestion"),
                func.count(func.unnest(Audiobook.genres)).label("count"),
                func.literal("genre").label("type"),
            )
            .filter(func.unnest(Audiobook.genres).ilike(f"{query}%"))
            .group_by(func.unnest(Audiobook.genres))
            .order_by(func.count(func.unnest(Audiobook.genres)).desc())
            .limit(limit // 3)
            .all()
        )

        # Combinaison des résultats
        all_suggestions = title_suggestions + author_suggestions + genre_suggestions
        suggestions = []

        for sugg in all_suggestions:
            suggestions.append(
                {"text": sugg.suggestion, "type": sugg.type, "count": sugg.count}
            )

        # Tri par nombre d'occurrences
        suggestions.sort(key=lambda x: x["count"], reverse=True)

        return AutoCompleteResponse(
            query=query, suggestions=suggestions[:limit], total_count=len(suggestions)
        )
