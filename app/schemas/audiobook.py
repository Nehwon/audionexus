"""
Schémas Pydantic pour la gestion des livres audio et leur synchronisation avec Audiobookshelf.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

# Modèles pour les métadonnées des livres audio
class AudiobookAuthor(BaseModel):
    """Auteur d'un livre audio."""
    name: str
    role: Optional[str] = None

class AudiobookNarrator(BaseModel):
    """Narrateur d'un livre audio."""
    name: str

class AudiobookSeries(BaseModel):
    """Série à laquelle appartient un livre audio."""
    name: str
    sequence: Optional[float] = None

class AudiobookTrack(BaseModel):
    """Piste audio d'un livre audio."""
    index: int
    filename: str
    duration: float
    size: int
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    channels: Optional[int] = None
    sample_rate: Optional[int] = None

class AudiobookChapter(BaseModel):
    """Chapitre d'un livre audio."""
    id: int
    start: float
    end: float
    title: str
    audio_file: Optional[str] = None

class AudiobookProgress(BaseModel):
    """Progression de lecture d'un utilisateur pour un livre audio."""
    user_id: str
    audiobook_id: str
    progress: float = Field(..., ge=0, le=1)
    current_time: float = Field(..., ge=0)
    is_finished: bool = False
    last_updated: datetime


class AudiobookProgressCreate(BaseModel):
    """Modèle pour la création d'une nouvelle entrée de progression de lecture."""
    user_id: str
    audiobook_id: str
    progress: float = Field(..., ge=0, le=1, description="Progression de lecture entre 0 et 1")
    current_time: float = Field(..., ge=0, description="Temps actuel de lecture en secondes")
    is_finished: bool = Field(False, description="Indique si le livre a été terminé")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Date de dernière mise à jour")


class AudiobookProgressUpdate(BaseModel):
    """Modèle pour la mise à jour d'une entrée de progression de lecture."""
    progress: Optional[float] = Field(None, ge=0, le=1, description="Nouvelle progression de lecture entre 0 et 1")
    current_time: Optional[float] = Field(None, ge=0, description="Nouveau temps de lecture en secondes")
    is_finished: Optional[bool] = Field(None, description="Indique si le livre a été terminé")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Date de dernière mise à jour")

# Modèles pour la création/mise à jour
class AudiobookBase(BaseModel):
    """Modèle de base pour un livre audio."""
    external_id: str
    source: str = "audiobookshelf"
    library_id: str
    title: str
    subtitle: Optional[str] = None
    authors: List[str] = []
    narrators: List[str] = []
    description: Optional[str] = None
    publisher: Optional[str] = None
    publish_year: Optional[int] = None
    genres: List[str] = []
    series: List[dict] = []
    language: str = "fr"
    isbn: Optional[str] = None
    duration: int = 0
    cover_path: Optional[str] = None
    audio_path: Optional[str] = None
    file_size: int = 0
    file_format: Optional[str] = None
    bitrate: int = 0
    channels: int = 2
    sample_rate: int = 44100
    is_explicit: bool = False
    is_abridged: bool = False
    tags: List[str] = []
    rating: float = 0.0
    num_tracks: int = 1
    track_number: int = 1
    disc_number: int = 1
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class AudiobookCreate(AudiobookBase):
    """Modèle pour la création d'un nouveau livre audio."""
    pass

class AudiobookUpdate(BaseModel):
    """Modèle pour la mise à jour partielle d'un livre audio."""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    authors: Optional[List[str]] = None
    narrators: Optional[List[str]] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    publish_year: Optional[int] = None
    genres: Optional[List[str]] = None
    series: Optional[List[dict]] = None
    language: Optional[str] = None
    isbn: Optional[str] = None
    duration: Optional[int] = None
    cover_path: Optional[str] = None
    is_explicit: Optional[bool] = None
    is_abridged: Optional[bool] = None
    tags: Optional[List[str]] = None
    rating: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class AudiobookInDB(AudiobookBase):
    """Modèle pour un livre audio en base de données."""
    id: int

    class Config:
        orm_mode = True

# Modèles pour les réponses API
class AudiobookResponse(AudiobookInDB):
    """Modèle de réponse pour un livre audio."""
    progress: Optional[float] = None
    is_new: bool = False

class AudiobookListResponse(BaseModel):
    """Modèle de réponse pour une liste de livres audio."""
    items: List[AudiobookResponse]
    total: int
    page: int
    size: int

# Modèles pour la synchronisation
class SyncStats(BaseModel):
    """Statistiques de synchronisation."""
    libraries_synced: int = 0
    audiobooks_synced: int = 0
    progress_updated: int = 0
    errors: int = 0

class SyncOptions(BaseModel):
    """Options de synchronisation."""
    full_sync: bool = False
    library_ids: Optional[List[str]] = None
    force_update: bool = False

# Modèles pour les requêtes API
audiobook_query_description = """
Filtres de recherche:
- q: Terme de recherche global (titre, auteur, description)
- author: Filtre par auteur
- series: Filtre par série
- genre: Filtre par genre
- min_duration: Durée minimale en secondes
- max_duration: Durée maximale en secondes
- sort: Champ de tri (title, author, duration, added_at, published_year)
- order: Ordre de tri (asc, desc)
"""

class AudiobookQuery(BaseModel):
    """Modèle pour les requêtes de recherche de livres audio."""
    q: Optional[str] = None
    author: Optional[str] = None
    series: Optional[str] = None
    genre: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    sort: str = "title"
    order: str = "asc"
    
    class Config:
        schema_extra = {
            "description": audiobook_query_description
        }
