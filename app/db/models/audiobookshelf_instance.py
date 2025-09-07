"""
Modèles SQLAlchemy pour la gestion des instances Audiobookshelf.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text

from app.db.database import Base


class AudiobookshelfInstance(Base):
    """Modèle pour une instance Audiobookshelf configurée."""

    __tablename__ = "audiobookshelf_instances"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(255), nullable=False, index=True
    )  # Nom descriptif de l'instance
    base_url = Column(
        String(512), nullable=False, index=True
    )  # URL de base de l'instance
    api_token = Column(Text, nullable=False)  # Token API chiffré
    username = Column(
        String(255), nullable=False
    )  # Nom d'utilisateur pour cette instance

    # Statut et configuration
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    sync_enabled = Column(
        Boolean, default=True, nullable=False, index=True
    )  # Instance éligible à la synchronisation
    priority = Column(
        Integer, default=1, nullable=False
    )  # Priorité pour le load balancing (1=haut, 10=bas)
    version = Column(String(50), nullable=True)  # Version de l'instance
    status = Column(
        String(20), default="unknown"
    )  # Statut de connexion: active, error, unknown

    # Métriques de performance et santé
    response_time_ms = Column(Integer, default=0)  # Temps de réponse moyen en ms
    health_check_timestamp = Column(DateTime, nullable=True)  # Dernier health check
    consecutive_failures = Column(Integer, default=0)  # Nombre d'échecs consécutifs

    # Gestion des erreurs et dernières activités
    last_sync = Column(DateTime, nullable=True)  # Dernière synchronisation réussie
    last_error = Column(Text, nullable=True)  # Dernière erreur rencontrée
    last_error_at = Column(DateTime, nullable=True)  # Date de la dernière erreur

    # Métadonnées système
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Index pour les performances
    __table_args__ = (
        Index("ix_audiobookshelf_instances_active", "is_active"),
        Index("ix_audiobookshelf_instances_sync_enabled", "sync_enabled"),
        Index("ix_audiobookshelf_instances_priority", "priority"),
        Index("ix_audiobookshelf_instances_url", "base_url"),
        Index("ix_audiobookshelf_instances_status", "status"),
        Index("ix_audiobookshelf_instances_health", "health_check_timestamp"),
    )

    def __repr__(self):
        return f"<AudiobookshelfInstance {self.id}: {self.name} ({self.status})>"

    def should_retry(self) -> bool:
        """
        Détermine si une nouvelle tentative de connexion devrait être faite
        basé sur la dernière erreur et les métriques de santé.

        Returns:
            bool: True si une retry est recommandée
        """
        if not self.last_error_at:
            return True

        # Calculer le temps écoulé depuis la dernière erreur
        elapsed = datetime.utcnow() - self.last_error_at

        # Prendre en compte les échecs consécutifs pour le backoff exponentiel
        backoff_multiplier = min(self.consecutive_failures, 5)  # Maximum 5x le délai

        # Retry après délai de base avec backoff pour erreurs temporaires
        if self.status == "error":
            base_delay = 300  # 5 minutes
            return elapsed.total_seconds() > (base_delay * (2**backoff_multiplier))
        elif self.status == "critical_error":
            base_delay = 1800  # 30 minutes
            return elapsed.total_seconds() > (base_delay * (2**backoff_multiplier))

        return True

    def get_health_score(self) -> float:
        """
        Calcule un score de santé pour l'instance basé sur divers métriques.

        Returns:
            float: Score de santé entre 0.0 (mauvais) et 1.0 (excellent)
        """
        score = 1.0

        # Pénalité pour le statut d'erreur
        if self.status == "error":
            score -= 0.3
        elif self.status == "critical_error":
            score -= 0.7

        # Pénalité pour les échecs consécutifs (maximum 0.3)
        failure_penalty = min(self.consecutive_failures * 0.1, 0.3)
        score -= failure_penalty

        # Pénalité pour les temps de réponse élevés (> 5s = pénalité complète)
        if self.response_time_ms > 5000:
            score -= 0.2
        elif self.response_time_ms > 2000:
            score -= 0.1
        elif self.response_time_ms > 1000:
            score -= 0.05

        # Pénalité pour les health checks vieux (> 10min = pénalité)
        if self.health_check_timestamp:
            health_age = (
                datetime.utcnow() - self.health_check_timestamp
            ).total_seconds()
            if health_age > 600:  # 10 minutes
                age_penalty = min(health_age / 3600 * 0.1, 0.2)  # Max 0.2 pour 2h
                score -= age_penalty

        # Assurer que le score reste entre 0 et 1
        return max(0.0, min(1.0, score))


# Mise à jour du fichier __init__.py pour importer les nouveaux modèles
__all__ = ["AudiobookshelfInstance"]
