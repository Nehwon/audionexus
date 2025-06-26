"""
Modèles de base de données pour l'application.
"""
from .base import (
    Base,
    User,
    UserBase,
    UserCreate,
    UserInDB,
    Token,
    TokenData,
    Book,
    BookBase,
    BookCreate,
    BookInDB,
    Library,
    LibraryBase,
    LibraryCreate,
    LibraryInDB,
    Chapter,
    Tag,
    Role,
    user_roles,
    book_tags
)

from .audiobook import Audiobook, AudiobookProgress

# Pour permettre l'importation directe depuis app.db.models
__all__ = [
    'Base',
    'User',
    'UserBase',
    'UserCreate',
    'UserInDB',
    'Token',
    'TokenData',
    'Book',
    'BookBase',
    'BookCreate',
    'BookInDB',
    'Library',
    'LibraryBase',
    'LibraryCreate',
    'LibraryInDB',
    'Chapter',
    'Tag',
    'Role',
    'Audiobook',
    'AudiobookProgress',
    'user_roles',
    'book_tags'
]
