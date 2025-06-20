"""
Opérations CRUD pour les utilisateurs.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.models.base import User, UserCreate

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Récupère un utilisateur par son ID.
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur
        
    Returns:
        User: L'utilisateur trouvé ou None
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Récupère un utilisateur par son email.
    
    Args:
        db: Session de base de données
        email: Email de l'utilisateur
        
    Returns:
        User: L'utilisateur trouvé ou None
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Récupère un utilisateur par son nom d'utilisateur.
    
    Args:
        db: Session de base de données
        username: Nom d'utilisateur
        
    Returns:
        User: L'utilisateur trouvé ou None
    """
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Crée un nouvel utilisateur.
    
    Args:
        db: Session de base de données
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
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe.
    
    Args:
        db: Session de base de données
        username: Nom d'utilisateur
        password: Mot de passe en clair
        
    Returns:
        User: L'utilisateur authentifié ou None
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Récupère une liste d'utilisateurs avec pagination.
    
    Args:
        db: Session de base de données
        skip: Nombre d'utilisateurs à sauter
        limit: Nombre maximum d'utilisateurs à retourner
        
    Returns:
        List[User]: Liste des utilisateurs
    """
    return db.query(User).offset(skip).limit(limit).all()

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
