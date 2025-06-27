from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, root_validator, ConfigDict, StringConstraints
from pydantic_core import PydanticCustomError

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur."""
    model_config = ConfigDict(from_attributes=True)
    
    username: Annotated[
        str, 
        StringConstraints(
            min_length=3, 
            max_length=50, 
            pattern=r'^[a-zA-Z0-9_]+$',
            to_lower=False
        )
    ]
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Valide la force du mot de passe."""
        if len(v) < 8:
            raise PydanticCustomError(
                'password_length',
                'Le mot de passe doit contenir au moins 8 caractères',
                {'min_length': 8}
            )
        if not any(c.isupper() for c in v):
            raise PydanticCustomError(
                'password_uppercase',
                'Le mot de passe doit contenir au moins une majuscule',
                {'error': 'no_uppercase'}
            )
        if not any(c.islower() for c in v):
            raise PydanticCustomError(
                'password_lowercase',
                'Le mot de passe doit contenir au moins une minuscule',
                {'error': 'no_lowercase'}
            )
        if not any(c.isdigit() for c in v):
            raise PydanticCustomError(
                'password_digit',
                'Le mot de passe doit contenir au moins un chiffre',
                {'error': 'no_digit'}
            )
        return v

class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur."""
    username: Optional[str] = Field(None, min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
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

class User(UserInDBBase):
    """Schéma pour la lecture d'un utilisateur (sans mot de passe)."""
    pass

class UserInDB(UserInDBBase):
    """Schéma pour un utilisateur en base de données (avec mot de passe hashé)."""
    hashed_password: str
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """Schéma pour le jeton d'accès."""
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    """Schéma pour les données du jeton."""
    email: Optional[str] = None
    user_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class RefreshTokenCreate(BaseModel):
    """Schéma pour la création d'un jeton de rafraîchissement."""
    token: str
    expires_at: datetime
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

class RefreshToken(RefreshTokenCreate):
    """Schéma pour la lecture d'un jeton de rafraîchissement."""
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
