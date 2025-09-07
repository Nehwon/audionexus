"""
Package pour les opérations CRUD (Create, Read, Update, Delete).
"""

# Livres audio
from .audiobook import (
    CRUDAudiobook,
    CRUDAudiobookProgress,
    audiobook,
    audiobook_progress,
)

# Utilisateurs
from .crud_user import (
    authenticate_user,
    create_user,
    get_user,
    get_user_by_email,
    get_user_by_username,
    get_users,
    is_active,
    is_superuser,
)

__all__ = [
    # Utilisateurs
    "get_user",
    "get_user_by_email",
    "get_user_by_username",
    "create_user",
    "authenticate_user",
    "get_users",
    "is_active",
    "is_superuser",
    # Livres audio
    "audiobook",
    "audiobook_progress",
    "CRUDAudiobook",
    "CRUDAudiobookProgress",
]
