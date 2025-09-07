"""
Service de gestion des permissions avec système d'autorisation granulaire.
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.base import (
    Permission,
    PermissionCreate,
    PermissionUpdate,
    Role,
    RoleCreate,
    RolePermission,
    User,
)

logger = logging.getLogger(__name__)


class PermissionService:
    """Service pour gérer les permissions et autorisations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """
        Crée une nouvelle permission.

        Args:
            permission_data: Données de la permission à créer

        Returns:
            Permission: La permission créée
        """
        # Vérifier si la permission existe déjà
        existing = await self.get_permission_by_codename(permission_data.codename)
        if existing:
            raise ValueError(
                f" Permission avec codename '{permission_data.codename}' existe déjà"
            )

        permission = Permission(**permission_data.model_dump())
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)

        logger.info(f"Permission créée: {permission.codename}")
        return permission

    async def get_permission_by_codename(self, codename: str) -> Optional[Permission]:
        """
        Récupère une permission par son codename.

        Args:
            codename: Codename de la permission

        Returns:
            Permission ou None
        """
        result = await self.db.execute(
            select(Permission).where(Permission.codename == codename)
        )
        return result.scalar_one_or_none()

    async def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """
        Récupère toutes les permissions pour une ressource donnée.

        Args:
            resource: Nom de la ressource

        Returns:
            Liste des permissions
        """
        result = await self.db.execute(
            select(Permission).where(Permission.resource == resource)
        )
        return result.scalars().all()

    async def update_permission(
        self, permission_id: int, permission_data: PermissionUpdate
    ) -> Optional[Permission]:
        """
        Met à jour une permission.

        Args:
            permission_id: ID de la permission à mettre à jour
            permission_data: Données de mise à jour

        Returns:
            Permission mise à jour ou None
        """
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            return None

        update_data = permission_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)

        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def delete_permission(self, permission_id: int) -> bool:
        """
        Supprime une permission.

        Args:
            permission_id: ID de la permission à supprimer

        Returns:
            True si supprimé, False sinon
        """
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            return False

        await self.db.delete(permission)
        await self.db.commit()
        return True

    async def create_role(self, role_data: RoleCreate) -> Role:
        """
        Crée un nouveau rôle avec ses permissions.

        Args:
            role_data: Données du rôle à créer

        Returns:
            Role: Le rôle créé
        """
        # Vérifier si le rôle existe déjà
        existing = await self.get_role_by_name(role_data.name)
        if existing:
            raise ValueError(f"Rôle '{role_data.name}' existe déjà")

        role = Role(name=role_data.name, description=role_data.description)
        self.db.add(role)
        await self.db.flush()  # Pour obtenir l'ID

        # Assigner les permissions si fournies
        if role_data.permission_ids:
            permissions = await self.db.execute(
                select(Permission).where(Permission.id.in_(role_data.permission_ids))
            )
            permissions = permissions.scalars().all()

            for permission in permissions:
                role_permission = RolePermission(role=role, permission=permission)
                self.db.add(role_permission)

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        Récupère un rôle par son nom.

        Args:
            name: Nom du rôle

        Returns:
            Role ou None
        """
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def assign_permissions_to_role(
        self, role_id: int, permission_ids: List[int]
    ) -> Optional[Role]:
        """
        Assigne des permissions à un rôle.

        Args:
            role_id: ID du rôle
            permission_ids: Liste des IDs des permissions

        Returns:
            Role mis à jour ou None
        """
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()

        if not role:
            return None

        # Supprimer les anciennes permissions
        await self.db.execute(
            select(RolePermission).where(RolePermission.role_id == role_id).delete()
        )

        # Ajouter les nouvelles permissions
        permissions = await self.db.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )
        permissions = permissions.scalars().all()

        for permission in permissions:
            role_permission = RolePermission(role=role, permission=permission)
            self.db.add(role_permission)

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def check_user_permission(
        self, user_id: int, permission_codename: str
    ) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique.

        Args:
            user_id: ID de l'utilisateur
            permission_codename: Codename de la permission

        Returns:
            True si l'utilisateur a la permission, False sinon
        """
        from sqlalchemy.orm import joinedload

        result = await self.db.execute(
            select(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        # Superuser a toutes les permissions
        if user.is_superuser:
            return True

        # Vérifier dans les rôles de l'utilisateur
        for role in user.roles:
            for role_permission in role.permissions:
                if role_permission.permission.codename == permission_codename:
                    return True

        return False

    async def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Récupère toutes les permissions d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Liste des codenames des permissions
        """
        from sqlalchemy.orm import joinedload

        result = await self.db.execute(
            select(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return []

        permissions = set()

        # Superuser a implicitement toutes les permissions
        if user.is_superuser:
            all_perms = await self.db.execute(select(Permission))
            permissions = {perm.codename for perm in all_perms.scalars().all()}
        else:
            for role in user.roles:
                for role_permission in role.permissions:
                    permissions.add(role_permission.permission.codename)

        return list(permissions)

    async def get_default_permissions(self) -> Dict[str, List[str]]:
        """
        Récupère les permissions par défaut pour les actions courantes.

        Returns:
            Dictionnaire avec les permissions par action
        """
        permissions = await self.db.execute(select(Permission))
        permissions = permissions.scalars().all()

        grouped = {}
        for perm in permissions:
            key = f"{perm.resource}.{perm.action}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(perm.codename)

        return grouped


# Permissions par défaut à créer lors de l'initialisation
DEFAULT_PERMISSIONS = [
    # Utilisateurs
    {
        "name": "Voir utilisateurs",
        "codename": "users.view",
        "resource": "users",
        "action": "view",
    },
    {
        "name": "Créer utilisateurs",
        "codename": "users.create",
        "resource": "users",
        "action": "create",
    },
    {
        "name": "Modifier utilisateurs",
        "codename": "users.update",
        "resource": "users",
        "action": "update",
    },
    {
        "name": "Supprimer utilisateurs",
        "codename": "users.delete",
        "resource": "users",
        "action": "delete",
    },
    {
        "name": "Assigner rôles",
        "codename": "users.assign_roles",
        "resource": "users",
        "action": "assign_roles",
    },
    {
        "name": "Changer mot de passe",
        "codename": "users.change_password",
        "resource": "users",
        "action": "change_password",
    },
    # Livres
    {
        "name": "Voir livres",
        "codename": "books.view",
        "resource": "books",
        "action": "view",
    },
    {
        "name": "Créer livres",
        "codename": "books.create",
        "resource": "books",
        "action": "create",
    },
    {
        "name": "Modifier livres",
        "codename": "books.update",
        "resource": "books",
        "action": "update",
    },
    {
        "name": "Supprimer livres",
        "codename": "books.delete",
        "resource": "books",
        "action": "delete",
    },
    # Bibliothèques
    {
        "name": "Voir bibliothèques",
        "codename": "libraries.view",
        "resource": "libraries",
        "action": "view",
    },
    {
        "name": "Créer bibliothèques",
        "codename": "libraries.create",
        "resource": "libraries",
        "action": "create",
    },
    {
        "name": "Modifier bibliothèques",
        "codename": "libraries.update",
        "resource": "libraries",
        "action": "update",
    },
    {
        "name": "Supprimer bibliothèques",
        "codename": "libraries.delete",
        "resource": "libraries",
        "action": "delete",
    },
    # Administration
    {
        "name": "Administration système",
        "codename": "admin.system",
        "resource": "admin",
        "action": "admin",
    },
    {
        "name": "Voir logs audit",
        "codename": "audit.view",
        "resource": "audit",
        "action": "view",
    },
]
