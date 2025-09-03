"""
Modèles SQLAlchemy pour la gestion des livres audio synchronisés avec Audiobookshelf.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, Float, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from app.db.database import Base

class Audiobook(Base):
    """Modèle de livre audio synchronisé avec Audiobookshelf."""
    __tablename__ = "audiobooks"
    
    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True, nullable=False)
    source = Column(String(50), default="audiobookshelf", nullable=False)
    
    # Métadonnées de base
    title = Column(String(255), nullable=False, index=True)
    subtitle = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    publisher = Column(String(255), nullable=True)
    publish_year = Column(Integer, nullable=True)
    isbn = Column(String(20), nullable=True, index=True)
    language = Column(String(10), default="fr", nullable=False)
    
    # Relations many-to-many via JSON
    authors = Column(JSON, default=list)  # Liste de noms d'auteurs
    narrators = Column(JSON, default=list)  # Liste de noms de narrateurs
    genres = Column(JSON, default=list)  # Liste de genres
    series = Column(JSON, default=list)  # Liste de dicts: [{"name": str, "sequence": float}]
    tags = Column(JSON, default=list)  # Liste de tags
    
    # Métadonnées techniques
    duration = Column(Integer, default=0)  # Durée en secondes
    file_size = Column(Integer, default=0)  # Taille en octets
    file_format = Column(String(50), nullable=True)  # Format du fichier (mp3, m4b, etc.)
    bitrate = Column(Integer, default=0)  # Débit binaire en kbps
    channels = Column(Integer, default=2)  # Nombre de canaux audio
    sample_rate = Column(Integer, default=44100)  # Taux d'échantillonnage en Hz
    
    # Métadonnées éditoriales
    is_explicit = Column(Boolean, default=False)
    is_abridged = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)  # Note moyenne sur 5
    
    # Numérotation
    num_tracks = Column(Integer, default=1)  # Nombre total de pistes
    track_number = Column(Integer, default=1)  # Numéro de piste
    disc_number = Column(Integer, default=1)  # Numéro de disque
    
    # Chemins
    cover_path = Column(String(512), nullable=True)  # Chemin vers l'image de couverture
    audio_path = Column(String(512), nullable=True)  # Chemin vers le fichier audio principal
    
    # Relations
    library_id = Column(String(100), nullable=False, index=True)  # ID de la bibliothèque dans Audiobookshelf
    
    # Métadonnées système
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_sync = Column(DateTime, nullable=True)  # Dernière synchronisation avec Audiobookshelf
    
    # Relations
    progress = relationship("AudiobookProgress", back_populates="audiobook", cascade="all, delete-orphan")
    
    # Index
    __table_args__ = (
        Index('ix_audiobooks_library_title', 'library_id', 'title'),
        Index('ix_audiobooks_author', 'authors'),
        Index('ix_audiobooks_genre', 'genres'),
        Index('ix_audiobooks_series', 'series'),
    )
    
    def __repr__(self):
        return f"<Audiobook {self.id}: {self.title}>"


class AudiobookProgress(Base):
    """Progression de lecture d'un utilisateur pour un livre audio."""
    __tablename__ = "audiobook_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    audiobook_id = Column(Integer, ForeignKey("audiobooks.id"), nullable=False, index=True)
    
    # Données de progression
    progress = Column(Float, default=0.0)  # Progression de 0 à 1
    current_time = Column(Float, default=0.0)  # Position actuelle en secondes
    is_finished = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_played = Column(DateTime, nullable=True)  # Dernière lecture
    
    # Relations
    audiobook = relationship("Audiobook", back_populates="progress")
    
    # Contrainte d'unicité
    __table_args__ = (
        UniqueConstraint('user_id', 'audiobook_id', name='_user_audiobook_uc'),
    )
    
    def __repr__(self):
        return f"<AudiobookProgress user:{self.user_id} book:{self.audiobook_id} {self.progress:.1%}>"


# Mise à jour du fichier __init__.py pour importer les nouveaux modèles
# Ceci sera utilisé par Alembic pour la détection des modèles
__all__ = ["Audiobook", "AudiobookProgress"]
