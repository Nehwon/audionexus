"""
Router FastAPI pour la gestion complète des utilisateurs, rôles et permissions.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_active_user
from app.services.user_service import UserService
from app.services.permission_service import PermissionService
from app.db.models.base import (
    User, Role, Permission, AuditLog,
    UserCreate, UserUpdate, UserInDB, RoleCreate, PermissionCreate,
    UserBase, RoleBase, PermissionBase
)
from app.crud.crud_user import get_users

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


async def require_permission(permission_codename: str):
    """
    Dépendance pour vérifier les permissions de l'utilisateur actuel.

    Args:
        permission_codename: Code de la permission requise

    Raises:
        HTTPException: Si l'utilisateur n'a pas la permission
    """
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
    ):
        permission_service = PermissionService(db)
        has_perm = await permission_service.check_user_permission(current_user.id, permission_codename)

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_codename}"
            )

        return current_user

    return permission_checker


# Routes pour les utilisateurs
@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_permission("users.create")),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée un nouvel utilisateur.

    Args:
        user: Données de l'utilisateur à créer
        current_user: Utilisateur actuel (doit avoir la permission users.create)

    Returns:
        User créé
    """
    try:
        user_service = UserService(db)
        created_user = await user_service.create_user(user, current_user.id)
        return UserInDB.model_validate(created_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la création d'utilisateur: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")


@router.get("/", response_model=List[UserInDB])
async def get_users_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    current_user: User = Depends(require_permission("users.view")),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère la liste des utilisateurs avec pagination.

    Args:
        skip: Nombre d'utilisateurs à sauter
        limit: Nombre maximum d'utilisateurs à retourner
        active_only: Retourner seulement les utilisateurs actifs
        current_user: Utilisateur actuel (doit avoir la permission users.view)

    Returns:
        Liste des utilisateurs
    """
    users = await get_users(db, skip=skip, limit=limit, active_only=active_only)
    return [UserInDB.model_validate(user) for user in users]


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère le profil de l'utilisateur actuel avec ses permissions.

    Args:
        current_user: Utilisateur actuel

    Returns:
        Profil utilisateur avec permissions
    """
    user_service = UserService(db)
    profile = await user_service.get_user_with_permissions(current_user.id)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return profile


@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("users.view")),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère un utilisateur par son ID.

    Args:
        user_id: ID de l'utilisateur
        current_user: Utilisateur actuel (doit avoir la permission users.view)

    Returns:
        Utilisateur demandé
    """
    from app.crud.crud_user import get_user as get_user_crud
    user = await get_user_crud(db, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserInDB.model_validate(user)


@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour un utilisateur.

    Args:
        user_id: ID de l'utilisateur à mettre à jour
        user_update: Données de mise à jour
        current_user: Utilisateur actuel

    Returns:
        Utilisateur mis à jour
    """
    # Vérifier les permissions (utilisateur peut se modifier lui-même, ou admin)
    permission_service = PermissionService(db)
    can_edit = (
        current_user.id == user_id or
        await permission_service.check_user_permission(current_user.id, "users.update")
    )

    if not can_edit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    user_service = UserService(db)
    updated_user = await user_service.update_user_profile(user_id, user_update, current_user.id)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserInDB.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("users.delete")),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprime un utilisateur (soft delete).

    Args:
        user_id: ID de l'utilisateur à supprimer
        current_user: Utilisateur actuel (doit avoir la permission users.delete)

    Returns:
        Réponse vide (204)
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    user_service = UserService(db)
    success = await user_service.delete_user(user_id, current_user.id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/{user_id}/roles", response_model=UserInDB)
async def assign_user_roles(
    user_id: int,
    role_ids: List[int],
    current_user: User = Depends(require_permission("users.assign_roles")),
    db: AsyncSession = Depends(get_db)
):
    """
    Assigne des rôles à un utilisateur.

    Args:
        user_id: ID de l'utilisateur
        role_ids: Liste des IDs des rôles à assigner
        current_user: Utilisateur actuel (doit avoir la permission users.assign_roles)

    Returns:
        Utilisateur mis à jour
    """
    user_service = UserService(db)
    updated_user = await user_service.assign_roles(user_id, role_ids, current_user.id)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserInDB.model_validate(updated_user)


@router.post("/{user_id}/change-password")
async def change_user_password(
    user_id: int,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change le mot de passe d'un utilisateur.

    Args:
        user_id: ID de l'utilisateur
        new_password: Nouveau mot de passe
        current_user: Utilisateur actuel

    Returns:
        Message de succès
    """
    # Vérifier les permissions
    permission_service = PermissionService(db)
    can_change = (
        current_user.id == user_id or
        await permission_service.check_user_permission(current_user.id, "users.change_password")
    )

    if not can_change:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    user_service = UserService(db)
    success = await user_service.change_password(user_id, new_password, current_user.id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Password changed successfully"}


# Routes pour les rôles
@router.post("/roles/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(require_permission("users.assign_roles")),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée un nouveau rôle.

    Args:
        role: Données du rôle à créer
        current_user: Utilisateur actuel (doit avoir la permission users.assign_roles)

    Returns:
        Rôle créé
    """
    try:
        permission_service = PermissionService(db)
        created_role = await permission_service.create_role(role)

        # Récupérer les permissions du rôle
        permissions = [perm.codename for perm in created_role.permissions]

        return {
            "role": RoleBase.model_validate(created_role),
            "permissions": permissions
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/roles/", response_model=List[Dict[str, Any]])
async def get_roles(
    current_user: User = Depends(require_permission("users.view")),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère tous les rôles avec leurs permissions.

    Args:
        current_user: Utilisateur actuel (doit avoir la permission users.view)

    Returns:
        Liste des rôles avec permissions
    """
    from sqlalchemy.orm import joinedload
    from sqlalchemy.future import select

    result = await db.execute(
        select(Role).options(joinedload(Role.permissions))
    )
    roles = result.unique().scalars().all()

    roles_data = []
    for role in roles:
        permissions = [perm.codename for perm in role.permissions]
        roles_data.append({
            "role": RoleBase.model_validate(role),
            "permissions": permissions,
            "user_count": len(role.users)
        })

    return roles_data


@router.post("/roles/{role_id}/permissions")
async def assign_role_permissions(
    role_id: int,
    permission_ids: List[int],
    current_user: User = Depends(require_permission("users.assign_roles")),
    db: AsyncSession = Depends(get_db)
):
    """
    Assigne des permissions à un rôle.

    Args:
        role_id: ID du rôle
        permission_ids: Liste des IDs des permissions
        current_user: Utilisateur actuel (doit avoir la permission users.assign_roles)

    Returns:
        Rôle mis à jour
    """
    permission_service = PermissionService(db)
    updated_role = await permission_service.assign_permissions_to_role(role_id, permission_ids)

    if not updated_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    return {"message": "Permissions assigned successfully"}


# Routes pour les permissions
@router.post("/permissions/", response_model=PermissionBase, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(require_permission("admin.system")),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée une nouvelle permission.

    Args:
        permission: Données de la permission à créer
        current_user: Utilisateur actuel (doit avoir la permission admin.system)

    Returns:
        Permission créée
    """
    try:
        permission_service = PermissionService(db)
        created_permission = await permission_service.create_permission(permission)
        return PermissionBase.model_validate(created_permission)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/permissions/", response_model=List[PermissionBase])
async def get_permissions(
    resource: Optional[str] = None,
    current_user: User = Depends(require_permission("users.view")),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère toutes les permissions, optionnellement filtrées par ressource.

    Args:
        resource: Ressource à filtrer (optionnel)
        current_user: Utilisateur actuel (doit avoir la permission users.view)

    Returns:
        Liste des permissions
    """
    from sqlalchemy.future import select

    query = select(Permission)
    if resource:
        query = query.where(Permission.resource == resource)

    result = await db.execute(query)
    permissions = result.scalars().all()

    return [PermissionBase.model_validate(perm) for perm in permissions]


# Routes pour l'audit
@router.get("/audit/", response_model=List[Dict[str, Any]])
async def get_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(require_permission("audit.view")),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les logs d'audit avec filtres optionnels.

    Args:
        user_id: ID de l'utilisateur à filtrer
        action: Action à filtrer
        resource: Ressource à filtrer
        skip: Nombre de logs à sauter
        limit: Nombre maximum de logs à retourner
        current_user: Utilisateur actuel (doit avoir la permission audit.view)

    Returns:
        Liste des logs d'audit
    """
    from sqlalchemy.future import select

    query = select(AuditLog).order_by(AuditLog.timestamp.desc())

    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource:
        query = query.where(AuditLog.resource == resource)

    result = await db.execute(query.offset(skip).limit(limit))
    audit_logs = result.scalars().all()

    return [log.to_dict() for log in audit_logs]


# Routes utilitaires
@router.get("/check-permission/{permission_codename}")
async def check_user_permission(
    permission_codename: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vérifie si l'utilisateur actuel a une permission spécifique.

    Args:
        permission_codename: Code de la permission à vérifier
        current_user: Utilisateur actuel

    Returns:
        Résultat du test de permission
    """
    permission_service = PermissionService(db)
    has_permission = await permission_service.check_user_permission(current_user.id, permission_codename)

    return {
        "permission": permission_codename,
        "has_permission": has_permission,
        "user_id": current_user.id
    }


@router.get("/my-permissions")
async def get_my_permissions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les permissions de l'utilisateur actuel.

    Args:
        current_user: Utilisateur actuel

    Returns:
        Liste des permissions de l'utilisateur
    """
    permission_service = PermissionService(db)
    permissions = await permission_service.get_user_permissions(current_user.id)

    return {
        "user_id": current_user.id,
        "permissions": permissions,
        "is_superuser": current_user.is_superuser
    }


# Middleware pour journaliser automatiquement les actions
@router.middleware("http")
async def audit_middleware(request, call_next):
    """Middleware pour journaliser automatiquement les actions utilisateur."""
    # Cette fonctionnalité serait implémentée avec un système de hooks
    # Pour l'instant, on laisse les services gérer l'audit directement
    response = await call_next(request)
    return response