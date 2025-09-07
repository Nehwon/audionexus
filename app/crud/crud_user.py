"""
Opérations CRUD pour les utilisateurs.
"""

from datetime import datetime
from typing import List, Optional

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
        full_name=user.full_name,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
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


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100, active_only: bool = True
) -> List[User]:
    """
    Récupère une liste d'utilisateurs avec pagination.

    Args:
        db: Session de base de données asynchrone
        skip: Nombre d'utilisateurs à sauter
        limit: Nombre maximum d'utilisateurs à retourner
        active_only: Retourner seulement les utilisateurs actifs

    Returns:
        List[User]: Liste des utilisateurs
    """
    query = select(User)
    if active_only:
        query = query.where(User.is_active == True)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user_data) -> Optional[User]:
    """
    Met à jour un utilisateur existant.

    Args:
        db: Session de base de données asynchrone
        user_id: ID de l'utilisateur à mettre à jour
        user_data: Données de mise à jour

    Returns:
        User: L'utilisateur mis à jour ou None
    """
    user = await get_user(db, user_id)
    if not user:
        return None

    # Mise à jour des champs fournis
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Supprime un utilisateur (soft delete en désactivant l'utilisateur).

    Args:
        db: Session de base de données asynchrone
        user_id: ID de l'utilisateur à supprimer

    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    user = await get_user(db, user_id)
    if not user:
        return False

    user.is_active = False
    user.updated_at = datetime.utcnow()
    await db.commit()
    return True


async def assign_roles_to_user(
    db: AsyncSession, user_id: int, role_ids: List[int]
) -> Optional[User]:
    """
    Assigne des rôles à un utilisateur.

    Args:
        db: Session de base de données asynchrone
        user_id: ID de l'utilisateur
        role_ids: Liste des IDs des rôles à assigner

    Returns:
        User: L'utilisateur mis à jour ou None
    """
    from app.db.models.base import Role

    user = await get_user(db, user_id)
    if not user:
        return None

    # Récupérer les rôles
    result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
    roles = result.scalars().all()

    # Mettre à jour les rôles de l'utilisateur
    user.roles = roles
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_permissions(db: AsyncSession, user_id: int) -> List[dict]:
    """
    Récupère les permissions d'un utilisateur via ses rôles.

    Args:
        db: Session de base de données asynchrone
        user_id: ID de l'utilisateur

    Returns:
        List[dict]: Liste des permissions
    """
    from sqlalchemy.orm import joinedload

    from app.db.models.base import Permission, RolePermission

    # Récupérer l'utilisateur avec ses rôles et permissions
    stmt = (
        select(User)
        .options(
            joinedload(User.roles)
            .joinedload("Role.permissions")
            .joinedload("RolePermission.permission")
        )
        .where(User.id == user_id)
    )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return []

    permissions = set()
    for role in user.roles:
        for role_perm in role.permissions:
            permissions.add(role_perm.permission.codename)

    return list(permissions)


def is_active(user: User) -> bool:
    """
    Vérifie si un utilisateur est actif.

    Args:
        user: Utilisateur à vérifier

    Returns:
        bool: True si l'utilisateur est actif, False sinon
    """
    return user.is_active and not user.is_account_locked()


def is_superuser(user: User) -> bool:
    """
    Vérifie si un utilisateur est un superutilisateur.

    Args:
        user: Utilisateur à vérifier

    Returns:
        bool: True si l'utilisateur est un superutilisateur, False sinon
    """
    return user.is_superuser


def has_permission(user: User, permission_codename: str) -> bool:
    """
    Vérifie si un utilisateur a une permission spécifique.

    Args:
        user: Utilisateur à vérifier
        permission_codename: Code de la permission à vérifier

    Returns:
        bool: True si l'utilisateur a la permission, False sinon
    """
    if user.is_superuser:
        return True

    # Vérifier dans les rôles de l'utilisateur
    for role in user.roles:
        for role_perm in role.permissions:
            if role_perm.permission.codename == permission_codename:
                return True

    return False
