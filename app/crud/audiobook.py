"""
Opérations CRUD pour la gestion des livres audio synchronisés avec Audiobookshelf.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session

from app.db.models.audiobook import Audiobook, AudiobookProgress
from app.schemas.audiobook import (
    AudiobookCreate,
    AudiobookInDB,
    AudiobookProgressCreate,
    AudiobookProgressUpdate,
    AudiobookQuery,
    AudiobookUpdate,
)

# Constantes pour les valeurs par défaut
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class CRUDAudiobook:
    """Opérations CRUD pour les livres audio."""

    @staticmethod
    def get(db: Session, audiobook_id: int) -> Optional[Audiobook]:
        """Récupère un livre audio par son ID."""
        return db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()

    @staticmethod
    def get_by_external_id(
        db: Session, external_id: str, source: str = "audiobookshelf"
    ) -> Optional[Audiobook]:
        """Récupère un livre audio par son ID externe et sa source."""
        return (
            db.query(Audiobook)
            .filter(Audiobook.external_id == external_id, Audiobook.source == source)
            .first()
        )

    @staticmethod
    def get_multi(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        query: Optional[AudiobookQuery] = None,
    ) -> tuple[List[Audiobook], int]:
        """Récupère plusieurs livres audio avec pagination et filtrage."""
        q = db.query(Audiobook)

        # Appliquer les filtres
        if query:
            if query.q:
                search = f"%{query.q}%"
                q = q.filter(
                    or_(
                        Audiobook.title.ilike(search),
                        Audiobook.description.ilike(search),
                        Audiobook.authors.op("@>")([query.q]),
                        Audiobook.series.op("@>")([{"name": query.q}]),
                    )
                )

            if query.author:
                q = q.filter(Audiobook.authors.op("@>")([query.author]))

            if query.genre:
                q = q.filter(Audiobook.genres.op("@>")([query.genre]))

            if query.series:
                q = q.filter(Audiobook.series.op("@>")([{"name": query.series}]))

            if query.min_duration is not None:
                q = q.filter(Audiobook.duration >= query.min_duration)

            if query.max_duration is not None:
                q = q.filter(Audiobook.duration <= query.max_duration)

            # Trier les résultats
            sort_field = getattr(Audiobook, query.sort, None)
            if sort_field is not None:
                sort_expr = (
                    sort_field.asc() if query.order == "asc" else sort_field.desc()
                )
                q = q.order_by(sort_expr)

        # Compter le nombre total d'éléments
        total = q.count()

        # Appliquer la pagination
        items = q.offset(skip).limit(limit).all()

        return items, total

    @staticmethod
    def create(
        db: Session, obj_in: Union[AudiobookCreate, Dict[str, Any]]
    ) -> Audiobook:
        """Crée un nouveau livre audio."""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)

        db_obj = Audiobook(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(
        db: Session,
        *,
        db_obj: Audiobook,
        obj_in: Union[AudiobookUpdate, Dict[str, Any]],
    ) -> Audiobook:
        """Met à jour un livre audio existant."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def remove(db: Session, *, id: int) -> Optional[Audiobook]:
        """Supprime un livre audio par son ID."""
        obj = db.query(Audiobook).get(id)
        if obj:
            db.delete(obj)
            db.commit()
            return obj
        return None

    @staticmethod
    def get_by_library(
        db: Session, library_id: str, *, skip: int = 0, limit: int = 100
    ) -> tuple[List[Audiobook], int]:
        """Récupère les livres audio d'une bibliothèque spécifique."""
        q = db.query(Audiobook).filter(Audiobook.library_id == library_id)
        total = q.count()
        items = q.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def search(
        db: Session,
        query: str,
        *,
        skip: int = 0,
        limit: int = 20,
        library_id: Optional[str] = None,
    ) -> tuple[List[Audiobook], int]:
        """Recherche des livres audio par terme de recherche."""
        search = f"%{query}%"
        q = db.query(Audiobook).filter(
            or_(
                Audiobook.title.ilike(search),
                Audiobook.subtitle.ilike(search),
                Audiobook.description.ilike(search),
                Audiobook.authors.op("@>")([query]),
                Audiobook.series.op("@>")([{"name": query}]),
                Audiobook.tags.op("@>")([query]),
            )
        )

        if library_id:
            q = q.filter(Audiobook.library_id == library_id)

        total = q.count()
        items = q.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def get_recently_added(
        db: Session, *, limit: int = 10, library_id: Optional[str] = None
    ) -> List[Audiobook]:
        """Récupère les livres audio récemment ajoutés."""
        q = db.query(Audiobook).order_by(Audiobook.created_at.desc())

        if library_id:
            q = q.filter(Audiobook.library_id == library_id)

        return q.limit(limit).all()

    @staticmethod
    def get_recently_updated(
        db: Session, *, limit: int = 10, library_id: Optional[str] = None
    ) -> List[Audiobook]:
        """Récupère les livres audio récemment mis à jour."""
        q = db.query(Audiobook).order_by(Audiobook.updated_at.desc())

        if library_id:
            q = q.filter(Audiobook.library_id == library_id)

        return q.limit(limit).all()


class CRUDAudiobookProgress:
    """Opérations CRUD pour la progression de lecture des livres audio."""

    @staticmethod
    def get_progress(
        db: Session, user_id: int, audiobook_id: int
    ) -> Optional[AudiobookProgress]:
        """Récupère la progression d'un utilisateur pour un livre audio."""
        return (
            db.query(AudiobookProgress)
            .filter(
                AudiobookProgress.user_id == user_id,
                AudiobookProgress.audiobook_id == audiobook_id,
            )
            .first()
        )

    @staticmethod
    def get_user_progress(
        db: Session,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        finished: Optional[bool] = None,
    ) -> tuple[List[AudiobookProgress], int]:
        """Récupère toutes les progressions d'un utilisateur."""
        q = db.query(AudiobookProgress).filter(AudiobookProgress.user_id == user_id)

        if finished is not None:
            q = q.filter(AudiobookProgress.is_finished == finished)

        total = q.count()
        items = q.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def create_progress(
        db: Session, *, obj_in: Union[AudiobookProgressCreate, Dict[str, Any]]
    ) -> AudiobookProgress:
        """Crée une nouvelle entrée de progression."""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)

        db_obj = AudiobookProgress(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_progress(
        db: Session,
        *,
        db_obj: AudiobookProgress,
        obj_in: Union[AudiobookProgressUpdate, Dict[str, Any]],
    ) -> AudiobookProgress:
        """Met à jour une progression existante."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        db_obj.last_played = datetime.utcnow()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_recently_played(
        db: Session, user_id: int, *, limit: int = 10
    ) -> List[AudiobookProgress]:
        """Récupère les livres audio récemment écoutés par un utilisateur."""
        return (
            db.query(AudiobookProgress)
            .filter(
                AudiobookProgress.user_id == user_id,
                AudiobookProgress.last_played.isnot(None),
            )
            .order_by(AudiobookProgress.last_played.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_in_progress(
        db: Session, user_id: int, *, limit: int = 10
    ) -> List[AudiobookProgress]:
        """Récupère les livres audio en cours d'écoute par un utilisateur."""
        return (
            db.query(AudiobookProgress)
            .filter(
                AudiobookProgress.user_id == user_id,
                AudiobookProgress.is_finished == False,  # noqa
                AudiobookProgress.progress > 0,
                AudiobookProgress.progress < 0.95,  # Exclure ceux presque terminés
            )
            .order_by(AudiobookProgress.updated_at.desc())
            .limit(limit)
            .all()
        )


# Instances pour une utilisation directe
audiobook = CRUDAudiobook()
audiobook_progress = CRUDAudiobookProgress()
