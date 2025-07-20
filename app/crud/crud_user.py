"""
Opérations CRUD pour les utilisateurs.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash, verify_password
from app.db.models.base import User, UserCreate

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Récupère un utilisateur par son ID.
    
    Args:
        db: Session de base de données asynchrone
        user_id: ID de l'utilisateur
        
    Returns:
        User: L'utilisateur trouvé ou None
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Récupère un utilisateur par son email.
    
    Args:
        db: Session de base de données asynchrone
        email: Email de l'utilisateur
        
    Returns:
        User: L'utilisateur trouvé ou None
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Récupère un utilisateur par son nom d'utilisateur.
    
    Args:
        db: Session de base de données asynchrone
        username: Nom d'utilisateur
        
    Returns:
        User: L'utilisateur trouvé ou None
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Crée un nouvel utilisateur.
    
    Args:
        db: Session de base de données asynchrone
        user: Données de l'utilisateur à créer
        
    Returns:
        User: L'utilisateur créé
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe.
    
    Args:
        db: Session de base de données asynchrone
        username: Nom d'utilisateur
        password: Mot de passe en clair
        
    Returns:
        User: L'utilisateur authentifié ou None
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Récupère une liste d'utilisateurs avec pagination.
    
    Args:
        db: Session de base de données asynchrone
        skip: Nombre d'utilisateurs à sauter
        limit: Nombre maximum d'utilisateurs à retourner
        
    Returns:
        List[User]: Liste des utilisateurs
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

def is_active(user: User) -> bool:
    """
    Vérifie si un utilisateur est actif.
    
    Args:
        user: Utilisateur à vérifier
        
    Returns:
        bool: True si l'utilisateur est actif, False sinon
    """
    return user.is_active

def is_superuser(user: User) -> bool:
    """
    Vérifie si un utilisateur est un superutilisateur.
    
    Args:
        user: Utilisateur à vérifier
        
    Returns:
        bool: True si l'utilisateur est un superutilisateur, False sinon
    """
    return user.is_superuser
