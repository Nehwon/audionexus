"""
Package pour les opérations CRUD (Create, Read, Update, Delete).
"""

# Utilisateurs
from .crud_user import (
    get_user,
    get_user_by_email,
    get_user_by_username,
    create_user,
    authenticate_user,
    get_users,
    is_active,
    is_superuser
)

# Livres audio
from .audiobook import (
    audiobook,
    audiobook_progress,
    CRUDAudiobook,
    CRUDAudiobookProgress
)

__all__ = [
    # Utilisateurs
    'get_user',
    'get_user_by_email',
    'get_user_by_username',
    'create_user',
    'authenticate_user',
    'get_users',
    'is_active',
    'is_superuser',
    
    # Livres audio
    'audiobook',
    'audiobook_progress',
    'CRUDAudiobook',
    'CRUDAudiobookProgress'
]
