"""
Service de gestion des utilisateurs avec fonctionnalités avancées.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.crud.crud_user import (
    get_user, get_users, update_user, delete_user, assign_roles_to_user,
    get_user_permissions, has_permission
)
from app.db.models.base import User, Role, Permission, AuditLog, UserCreate, UserUpdate
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


class UserService:
    """Service pour la gestion complète des utilisateurs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate, created_by: Optional[int] = None) -> User:
        """
        Crée un nouvel utilisateur avec vérifications.

        Args:
            user_data: Données de l'utilisateur à créer
            created_by: ID de l'utilisateur qui crée cet utilisateur

        Returns:
            User: L'utilisateur créé
        """
        # Vérifier si l'utilisateur existe déjà
        existing = await get_user_by_email(self.db, user_data.email)
        if existing:
            raise ValueError("Un utilisateur avec cet email existe déjà")

        existing = await get_user_by_username(self.db, user_data.username)
        if existing:
            raise ValueError("Un utilisateur avec ce nom d'utilisateur existe déjà")

        # Créer l'utilisateur
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict['hashed_password'] = hashed_password
        del user_dict['password']

        db_user = User(**user_dict)
        self.db.add(db_user)
        await self.db.flush()  # Pour obtenir l'ID

        # Journaliser la création
        await self._log_action(
            user_id=db_user.id,
            action='create',
            resource='users',
            resource_id=str(db_user.id),
            details={'created_by': created_by},
            performed_by=created_by
        )

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update_user_profile(self, user_id: int, user_data: UserUpdate, updated_by: Optional[int] = None) -> Optional[User]:
        """
        Met à jour le profil d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur à mettre à jour
            user_data: Données de mise à jour
            updated_by: ID de l'utilisateur effectuant la mise à jour

        Returns:
            User: L'utilisateur mis à jour ou None
        """
        # Vérifier les permissions
        if updated_by and updated_by != user_id:
            updater = await get_user(self.db, updated_by)
            if not (updater and (updater.is_superuser or has_permission(updater, 'users.update'))):
                raise PermissionError("Permission denied")

        # Récupérer les anciennes données pour l'audit
        old_user = await get_user(self.db, user_id)
        if not old_user:
            return None

        # Mettre à jour l'utilisateur
        updated_user = await update_user(self.db, user_id, user_data)
        if updated_user:
            # Journaliser la mise à jour
            changes = {}
            for field in user_data.model_fields:
                old_value = getattr(old_user, field, None)
                new_value = getattr(updated_user, field, None)
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}

            await self._log_action(
                user_id=user_id,
                action='update',
                resource='users',
                resource_id=str(user_id),
                details={'changes': changes},
                performed_by=updated_by
            )

        return updated_user

    async def delete_user(self, user_id: int, deleted_by: int) -> bool:
        """
        Supprime un utilisateur (soft delete).

        Args:
            user_id: ID de l'utilisateur à supprimer
            deleted_by: ID de l'utilisateur effectuant la suppression

        Returns:
            bool: True si la suppression a réussi
        """
        # Vérifier les permissions
        deleter = await get_user(self.db, deleted_by)
        if not (deleter and (deleter.is_superuser or has_permission(deleter, 'users.delete'))):
            raise PermissionError("Permission denied")

        # Empêcher la suppression de soi-même
        if deleted_by == user_id:
            raise ValueError("Impossible de se supprimer soi-même")

        success = await delete_user(self.db, user_id)
        if success:
            await self._log_action(
                user_id=user_id,
                action='delete',
                resource='users',
                resource_id=str(user_id),
                details={'deleted_by': deleted_by},
                performed_by=deleted_by
            )

        return success

    async def assign_roles(self, user_id: int, role_ids: List[int], assigned_by: int) -> Optional[User]:
        """
        Assigne des rôles à un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            role_ids: Liste des IDs des rôles à assigner
            assigned_by: ID de l'utilisateur effectuant l'assignation

        Returns:
            User: L'utilisateur mis à jour ou None
        """
        # Vérifier les permissions
        assigner = await get_user(self.db, assigned_by)
        if not (assigner and (assigner.is_superuser or has_permission(assigner, 'users.assign_roles'))):
            raise PermissionError("Permission denied")

        # Récupérer les anciens rôles pour l'audit
        old_user = await get_user(self.db, user_id)
        if not old_user:
            return None

        old_role_names = [role.name for role in old_user.roles]

        # Assigner les rôles
        updated_user = await assign_roles_to_user(self.db, user_id, role_ids)
        if updated_user:
            new_role_names = [role.name for role in updated_user.roles]

            await self._log_action(
                user_id=user_id,
                action='assign_roles',
                resource='users',
                resource_id=str(user_id),
                details={
                    'old_roles': old_role_names,
                    'new_roles': new_role_names,
                    'assigned_by': assigned_by
                },
                performed_by=assigned_by
            )

        return updated_user

    async def change_password(self, user_id: int, new_password: str, changed_by: Optional[int] = None) -> bool:
        """
        Change le mot de passe d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            new_password: Nouveau mot de passe
            changed_by: ID de l'utilisateur effectuant le changement

        Returns:
            bool: True si le changement a réussi
        """
        # Vérifier les permissions
        if changed_by and changed_by != user_id:
            changer = await get_user(self.db, changed_by)
            if not (changer and (changer.is_superuser or has_permission(changer, 'users.change_password'))):
                raise PermissionError("Permission denied")

        user = await get_user(self.db, user_id)
        if not user:
            return False

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()

        await self.db.commit()

        await self._log_action(
            user_id=user_id,
            action='change_password',
            resource='users',
            resource_id=str(user_id),
            details={'changed_by': changed_by},
            performed_by=changed_by
        )

        return True

    async def get_user_with_permissions(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur avec ses permissions.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Dict avec les données utilisateur et permissions
        """
        user = await get_user(self.db, user_id)
        if not user:
            return None

        permissions = await get_user_permissions(self.db, user_id)

        return {
            'user': user.to_dict(),
            'roles': [{'id': role.id, 'name': role.name, 'description': role.description} for role in user.roles],
            'permissions': permissions
        }

    async def _log_action(self, user_id: int, action: str, resource: str,
                         resource_id: Optional[str] = None, details: Optional[Dict] = None,
                         performed_by: Optional[int] = None):
        """
        Journalise une action dans le système d'audit.

        Args:
            user_id: ID de l'utilisateur concerné par l'action
            action: Type d'action
            resource: Ressource concernée
            resource_id: ID de la ressource
            details: Détails supplémentaires
            performed_by: ID de l'utilisateur qui a effectué l'action
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details or {},
            performed_by=performed_by
        )

        self.db.add(audit_log)
        # Ne pas committer ici, laisser le commit global gérer


# Fonctions utilitaires pour la compatibilité avec crud
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Récupère un utilisateur par email."""
    from app.crud.crud_user import get_user_by_email
    return await get_user_by_email(db, email)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Récupère un utilisateur par nom d'utilisateur."""
    from app.crud.crud_user import get_user_by_username
    return await get_user_by_username(db, username)