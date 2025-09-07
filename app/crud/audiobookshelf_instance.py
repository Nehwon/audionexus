"""
Operations CRUD pour les instances Audiobookshelf.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models.audiobookshelf_instance import AudiobookshelfInstance


class CRUDAudiobookshelfInstance:
    """Operations CRUD pour les instances Audiobookshelf."""

    @staticmethod
    def get(db: Session, instance_id: int) -> Optional[AudiobookshelfInstance]:
        """
        Récupère une instance par son ID.

        Args:
            db: Session de base de données
            instance_id: ID de l'instance

        Returns:
            Instance trouvée ou None
        """
        return db.query(AudiobookshelfInstance).filter_by(id=instance_id).first()

    @staticmethod
    def get_by_url(db: Session, base_url: str) -> Optional[AudiobookshelfInstance]:
        """
        Récupère une instance par son URL.

        Args:
            db: Session de base de données
            base_url: URL de l'instance

        Returns:
            Instance trouvée ou None
        """
        return db.query(AudiobookshelfInstance).filter_by(base_url=base_url).first()

    @staticmethod
    def get_multi(
        db: Session, *, skip: int = 0, limit: int = 100, only_active: bool = False
    ) -> List[AudiobookshelfInstance]:
        """
        Récupère une liste d'instances avec pagination.

        Args:
            db: Session de base de données
            skip: Nombre d'éléments à ignorer
            limit: Nombre maximum d'éléments à retourner
            only_active: Ne retourner que les instances actives

        Returns:
            Liste des instances
        """
        query = db.query(AudiobookshelfInstance)
        if only_active:
            query = query.filter_by(is_active=True)
        return (
            query.order_by(AudiobookshelfInstance.name).offset(skip).limit(limit).all()
        )

    @staticmethod
    def get_active_instances(db: Session) -> List[AudiobookshelfInstance]:
        """
        Récupère toutes les instances actives.

        Args:
            db: Session de base de données

        Returns:
            Liste des instances actives
        """
        return (
            db.query(AudiobookshelfInstance)
            .filter_by(is_active=True)
            .order_by(AudiobookshelfInstance.name)
            .all()
        )

    @staticmethod
    def get_instances_with_errors(db: Session) -> List[AudiobookshelfInstance]:
        """
        Récupère les instances qui ont des erreurs récentes.

        Args:
            db: Session de base de données

        Returns:
            Liste des instances avec erreurs
        """
        return (
            db.query(AudiobookshelfInstance)
            .filter(AudiobookshelfInstance.status.in_(["error", "critical_error"]))
            .order_by(AudiobookshelfInstance.last_error_at.desc())
            .all()
        )

    @staticmethod
    def create(db: Session, *, obj_in: Dict[str, Any]) -> AudiobookshelfInstance:
        """
        Crée une nouvelle instance.

        Args:
            db: Session de base de données
            obj_in: Données pour la création

        Returns:
            Instance créée
        """
        db_obj = AudiobookshelfInstance(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(
        db: Session, *, db_obj: AudiobookshelfInstance, obj_in: Dict[str, Any]
    ) -> AudiobookshelfInstance:
        """
        Met à jour une instance existante.

        Args:
            db: Session de base de données
            db_obj: Instance à mettre à jour
            obj_in: Données de mise à jour

        Returns:
            Instance mise à jour
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db_obj.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def remove(db: Session, *, instance_id: int) -> Optional[AudiobookshelfInstance]:
        """
        Supprime une instance par son ID.

        Args:
            db: Session de base de données
            instance_id: ID de l'instance à supprimer

        Returns:
            Instance supprimée ou None si non trouvée
        """
        obj = db.query(AudiobookshelfInstance).get(instance_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    @staticmethod
    def update_connection_status(
        db: Session,
        *,
        instance_id: int,
        status: str,
        version: Optional[str] = None,
        error: Optional[str] = None,
    ) -> bool:
        """
        Met à jour le statut de connexion d'une instance.

        Args:
            db: Session de base de données
            instance_id: ID de l'instance
            status: Nouveau statut
            version: Version détectée (optionnel)
            error: Erreur rencontrée (optionnel)

        Returns:
            True si mise à jour réussie
        """
        obj = db.query(AudiobookshelfInstance).get(instance_id)
        if not obj:
            return False

        obj.status = status

        if version is not None:
            obj.version = version

        if error is not None:
            obj.last_error = error
            obj.last_error_at = datetime.utcnow()
        else:
            # Si pas d'erreur, réinitialiser les champs d'erreur
            if status == "active":
                obj.last_error = None
                obj.last_error_at = None

        if status == "active":
            obj.last_sync = datetime.utcnow()

        db.commit()
        return True

    @staticmethod
    def get_instances_summary(db: Session) -> Dict[str, int]:
        """
        Récupère un résumé des instances.

        Args:
            db: Session de base de données

        Returns:
            Dictionnaire avec les statistiques
        """
        total = db.query(AudiobookshelfInstance).count()
        active = db.query(AudiobookshelfInstance).filter_by(is_active=True).count()
        with_errors = (
            db.query(AudiobookshelfInstance)
            .filter(AudiobookshelfInstance.status.in_(["error", "critical_error"]))
            .count()
        )

        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "with_errors": with_errors,
        }


crud_audiobookshelf_instance = CRUDAudiobookshelfInstance()


__all__ = ["crud_audiobookshelf_instance", "CRUDAudiobookshelfInstance"]
