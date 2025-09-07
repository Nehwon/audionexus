"""
Modèles de base de données pour l'application.
"""

from .audiobook import Audiobook, AudiobookProgress
from .base import (
    Base,
    Book,
    BookBase,
    BookCreate,
    BookInDB,
    Chapter,
    Library,
    LibraryBase,
    LibraryCreate,
    LibraryInDB,
    Role,
    Tag,
    Token,
    TokenData,
    User,
    UserBase,
    UserCreate,
    UserInDB,
    book_tags,
    user_roles,
)
from .search import SearchHistory, SearchSuggestion

# Pour permettre l'importation directe depuis app.db.models
__all__ = [
    "Base",
    "User",
    "UserBase",
    "UserCreate",
    "UserInDB",
    "Token",
    "TokenData",
    "Book",
    "BookBase",
    "BookCreate",
    "BookInDB",
    "Library",
    "LibraryBase",
    "LibraryCreate",
    "LibraryInDB",
    "Chapter",
    "Tag",
    "Role",
    "Audiobook",
    "AudiobookProgress",
    "SearchHistory",
    "SearchSuggestion",
    "user_roles",
    "book_tags",
]
