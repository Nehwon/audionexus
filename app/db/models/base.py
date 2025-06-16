"""
Modèles de base de données SQLAlchemy pour l'application de gestion d'audiobooks.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, Float, JSON, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel, EmailStr, Field

# Déclaration de la base pour les modèles SQLAlchemy
Base = declarative_base()

# Table d'association pour la relation many-to-many entre utilisateurs et rôles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

# Table d'association pour la relation many-to-many entre livres et étiquettes
book_tags = Table(
    'book_tags',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class User(Base):
    """Modèle utilisateur pour l'authentification et l'autorisation."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    books = relationship('Book', back_populates='owner')
    libraries = relationship('Library', back_populates='owner')


class Role(Base):
    """Modèle de rôles pour les utilisateurs."""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    
    # Relations
    users = relationship('User', secondary=user_roles, back_populates='roles')


class Library(Base):
    """Modèle de bibliothèque d'audiobooks."""
    __tablename__ = 'libraries'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    path = Column(String(255), nullable=False, unique=True)
    is_public = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    owner = relationship('User', back_populates='libraries')
    books = relationship('Book', back_populates='library', cascade='all, delete-orphan')


class Book(Base):
    """Modèle de livre audio."""
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255))
    authors = Column(JSON)  # Liste des auteurs
    narrators = Column(JSON)  # Liste des narrateurs
    series = Column(JSON)  # Informations sur la série
    description = Column(Text)
    publisher = Column(String(255))
    publish_year = Column(Integer)
    genres = Column(JSON)  # Liste des genres
    duration = Column(Integer)  # Durée en secondes
    size = Column(Integer)  # Taille en octets
    path = Column(String(255), nullable=False)
    cover_path = Column(String(255))
    isbn = Column(String(20))
    language = Column(String(10))
    explicit = Column(Boolean, default=False)
    abridged = Column(Boolean, default=False)
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    library = relationship('Library', back_populates='books')
    owner = relationship('User', back_populates='books')
    tags = relationship('Tag', secondary=book_tags, back_populates='books')
    chapters = relationship('Chapter', back_populates='book', cascade='all, delete-orphan')


class Chapter(Base):
    """Modèle de chapitre de livre audio."""
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start_time = Column(Float, nullable=False)  # En secondes
    end_time = Column(Float, nullable=False)  # En secondes
    file_path = Column(String(255), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    
    # Relations
    book = relationship('Book', back_populates='chapters')


class Tag(Base):
    """Modèle d'étiquettes pour les livres audio."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    books = relationship('Book', secondary=book_tags, back_populates='tags')


# Modèles Pydantic pour la validation des données
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class BookBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    authors: List[str] = []
    narrators: List[str] = []
    description: Optional[str] = None
    publisher: Optional[str] = None
    publish_year: Optional[int] = None
    genres: List[str] = []
    isbn: Optional[str] = None
    language: str = "fr"
    explicit: bool = False
    abridged: bool = False


class BookCreate(BookBase):
    library_id: int
    path: str


class BookInDB(BookBase):
    id: int
    duration: int
    size: int
    cover_path: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LibraryBase(BaseModel):
    name: str
    description: Optional[str] = None
    path: str
    is_public: bool = False


class LibraryCreate(LibraryBase):
    pass


class LibraryInDB(LibraryBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
