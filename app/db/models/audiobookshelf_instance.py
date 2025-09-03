"""
Modèles SQLAlchemy pour la gestion des instances Audiobookshelf.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index

from app.db.database import Base


class AudiobookshelfInstance(Base):
    """Modèle pour une instance Audiobookshelf configurée."""
    __tablename__ = "audiobookshelf_instances"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)  # Nom descriptif de l'instance
    base_url = Column(String(512), nullable=False, index=True)  # URL de base de l'instance
    api_token = Column(Text, nullable=False)  # Token API chiffré
    username = Column(String(255), nullable=False)  # Nom d'utilisateur pour cette instance

    # Statut et configuration
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    version = Column(String(50), nullable=True)  # Version de l'instance
    status = Column(String(20), default="unknown")  # Statut de connexion: active, error, unknown

    # Gestion des erreurs et dernières activités
    last_sync = Column(DateTime, nullable=True)  # Dernière synchronisation réussie
    last_error = Column(Text, nullable=True)  # Dernière erreur rencontrée
    last_error_at = Column(DateTime, nullable=True)  # Date de la dernière erreur

    # Métadonnées système
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Index pour les performances
    __table_args__ = (
        Index('ix_audiobookshelf_instances_active', 'is_active'),
        Index('ix_audiobookshelf_instances_url', 'base_url'),
        Index('ix_audiobookshelf_instances_status', 'status'),
    )

    def __repr__(self):
        return f"<AudiobookshelfInstance {self.id}: {self.name} ({self.status})>"

    def should_retry(self) -> bool:
        """
        Détermine si une nouvelle tentative de connexion devrait être faite
        basé sur la dernière erreur.

        Returns:
            bool: True si une retry est recommandée
        """
        if not self.last_error_at:
            return True

        # Calculer le temps écoulé depuis la dernière erreur
        elapsed = datetime.utcnow() - self.last_error_at

        # Retry après 5min pour erreurs temporaires, 30min pour erreurs critiques
        if self.status == "error":
            return elapsed.total_seconds() > 300  # 5 minutes
        elif self.status == "critical_error":
            return elapsed.total_seconds() > 1800  # 30 minutes

        return True


# Mise à jour du fichier __init__.py pour importer les nouveaux modèles
__all__ = ["AudiobookshelfInstance"]