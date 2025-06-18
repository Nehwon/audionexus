from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        """Valide la force du mot de passe."""
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(c.islower() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v

class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDBBase(UserBase):
    """Schéma de base pour un utilisateur en base de données."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    """Schéma pour la lecture d'un utilisateur (sans mot de passe)."""
    pass

class UserInDB(UserInDBBase):
    """Schéma pour un utilisateur en base de données (avec mot de passe hashé)."""
    hashed_password: str

class Token(BaseModel):
    """Schéma pour le jeton d'accès."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schéma pour les données du jeton."""
    email: Optional[str] = None
    user_id: Optional[int] = None

class RefreshTokenCreate(BaseModel):
    """Schéma pour la création d'un jeton de rafraîchissement."""
    token: str
    expires_at: datetime
    user_id: int

class RefreshToken(RefreshTokenCreate):
    """Schéma pour la lecture d'un jeton de rafraîchissement."""
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
