"""
Modèles de données pour l'intégration avec VoidAuth.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    """Modèle pour la création d'un utilisateur."""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: bool = True
    email_verified: bool = False
    attributes: Optional[Dict[str, Any]] = None

class UserUpdate(BaseModel):
    """Modèle pour la mise à jour d'un utilisateur."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: Optional[bool] = None
    email_verified: Optional[bool] = None
    attributes: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    """Modèle de réponse pour les informations d'un utilisateur."""
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: bool
    email_verified: bool
    created_timestamp: Optional[datetime] = None
    attributes: Optional[Dict[str, Any]] = {}

class TokenResponse(BaseModel):
    """Modèle de réponse pour les tokens d'authentification."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int

class Role(BaseModel):
    """Modèle pour un rôle d'utilisateur."""
    id: str
    name: str
    description: Optional[str] = None
    composite: bool = False
    client_role: bool = False
    container_id: Optional[str] = None

class Permission(BaseModel):
    """Modèle pour une permission."""
    id: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    logic: Optional[str] = None
    decision_strategy: Optional[str] = None
