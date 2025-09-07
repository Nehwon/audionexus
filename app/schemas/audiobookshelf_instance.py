"""
Schemas Pydantic pour les instances Audiobookshelf.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class AudiobookshelfInstanceBase(BaseModel):
    """Schema de base pour une instance Audiobookshelf."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Nom descriptif de l'instance"
    )
    base_url: str = Field(
        ..., description="URL de base de l'instance (ex: https://books.example.com)"
    )
    username: str = Field(
        ..., min_length=1, max_length=255, description="Nom d'utilisateur"
    )


class AudiobookshelfInstanceCreate(AudiobookshelfInstanceBase):
    """Schema pour la création d'une instance."""

    password: str = Field(
        ..., min_length=1, description="Mot de passe pour l'authentification"
    )

    @validator("base_url")
    def validate_base_url(cls, v):
        """Valide et normalise l'URL."""
        if not v:
            raise ValueError("URL requise")
        # Supprimer le '/' final et valider le format
        url = v.rstrip("/")
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        return url


class AudiobookshelfInstanceUpdate(BaseModel):
    """Schema pour la mise à jour d'une instance."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    base_url: Optional[str] = None
    is_active: Optional[bool] = None

    @validator("base_url")
    def validate_base_url(cls, v):
        """Valide et normalise l'URL."""
        if v is None:
            return v
        url = v.rstrip("/")
        if url and not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        return url


class AudiobookshelfInstanceTokenRotate(BaseModel):
    """Schema pour la rotation d'un token."""

    password: str = Field(
        ...,
        min_length=1,
        description="Nouveau mot de passe pour obtenir un nouveau token",
    )


class AudiobookshelfInstanceResponse(AudiobookshelfInstanceBase):
    """Schema de réponse pour une instance."""

    id: int
    is_active: bool
    version: Optional[str]
    status: str
    last_sync: Optional[datetime]
    last_error: Optional[str]
    last_error_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AudiobookshelfInstanceSummary(BaseModel):
    """Schema résumé pour la liste des instances."""

    id: int
    name: str
    base_url: str
    username: str
    is_active: bool
    status: str
    version: Optional[str]
    last_sync: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


class AudiobookshelfInstanceTestResponse(BaseModel):
    """Schema pour la réponse d'un test de connexion."""

    success: bool
    version: Optional[str] = None
    status: str
    error: Optional[str] = None
    last_sync: Optional[datetime] = None


class AudiobookshelfInstanceList(BaseModel):
    """Schema pour la liste des instances."""

    instances: list[AudiobookshelfInstanceSummary]
    total: int
    active: int


# Schemas pour l'authentification (non stockés)
class AudiobookshelfAuthRequest(BaseModel):
    """Schema pour une requête d'authentification."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AudiobookshelfAuthResponse(BaseModel):
    """Schema pour la réponse d'authentification."""

    success: bool
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


__all__ = [
    "AudiobookshelfInstanceCreate",
    "AudiobookshelfInstanceUpdate",
    "AudiobookshelfInstanceResponse",
    "AudiobookshelfInstanceSummary",
    "AudiobookshelfInstanceTestResponse",
    "AudiobookshelfInstanceList",
    "AudiobookshelfAuthRequest",
    "AudiobookshelfAuthResponse",
    "AudiobookshelfInstanceTokenRotate",
]
