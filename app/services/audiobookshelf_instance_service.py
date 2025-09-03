"""
Service pour la gestion des instances Audiobookshelf et de leurs tokens.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from sqlalchemy.orm import Session

from app.core.security import encrypt_token, decrypt_token
from app.db.models.audiobookshelf_instance import AudiobookshelfInstance
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class AudiobookshelfInstanceService:
    """Service pour gestion des instances Audiobookshelf."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def __del__(self):
        if hasattr(self, 'db') and self.db:
            self.db.close()

    def create_instance(
        self,
        name: str,
        base_url: str,
        username: str,
        password: str
    ) -> Optional[AudiobookshelfInstance]:
        """
        Crée une nouvelle instance Audiobookshelf avec authentification.

        Args:
            name: Nom descriptif de l'instance
            base_url: URL de base de l'instance (ex: https://books.example.com)
            username: Nom d'utilisateur
            password: Mot de passe

        Returns:
            AudiobookshelfInstance créée ou None en cas d'échec
        """
        try:
            # Tester la connexion et obtenir le token
            token = self._authenticate_instance(base_url, username, password)
            if not token:
                logger.error(f"Impossible d'authentifier l'instance {name}")
                return None

            # Vérifier la validité de l'instance
            version, status = self._test_instance_connection(base_url, token, username)

            # Chiffrer le token avant stockage
            encrypted_token = encrypt_token(token)

            # Créer l'instance en base
            db_instance = AudiobookshelfInstance(
                name=name,
                base_url=base_url.rstrip('/'),  # Supprimer le '/' final si présent
                api_token=encrypted_token,
                username=username,
                version=version,
                status=status,
                is_active=True,
                last_sync=None,
                last_error=None,
                last_error_at=None
            )

            self.db.add(db_instance)
            self.db.commit()
            self.db.refresh(db_instance)

            logger.info(f"Instance {name} créée avec succès")
            return db_instance

        except Exception as e:
            logger.error(f"Erreur lors de la création de l'instance {name}: {str(e)}")
            self.db.rollback()
            return None

    def get_instance(self, instance_id: int) -> Optional[AudiobookshelfInstance]:
        """
        Récupère une instance par son ID.

        Args:
            instance_id: ID de l'instance

        Returns:
            Instance trouvée ou None
        """
        return self.db.query(AudiobookshelfInstance).filter_by(id=instance_id).first()

    def get_instances(self, only_active: bool = True) -> List[AudiobookshelfInstance]:
        """
        Récupère toutes les instances (actives par défaut).

        Args:
            only_active: Ne retourner que les instances actives

        Returns:
            Liste des instances
        """
        query = self.db.query(AudiobookshelfInstance)
        if only_active:
            query = query.filter_by(is_active=True)
        return query.order_by(AudiobookshelfInstance.name).all()

    def update_instance(
        self,
        instance_id: int,
        name: Optional[str] = None,
        base_url: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        Met à jour une instance existante.

        Args:
            instance_id: ID de l'instance
            name: Nouveau nom (optionnel)
            base_url: Nouvelle URL (optionnel)
            is_active: Nouveau statut d'activité (optionnel)

        Returns:
            True si mise à jour réussie
        """
        try:
            instance = self.get_instance(instance_id)
            if not instance:
                return False

            updated = False
            if name is not None:
                instance.name = name
                updated = True
            if base_url is not None:
                instance.base_url = base_url.rstrip('/')
                updated = True
            if is_active is not None:
                instance.is_active = is_active
                updated = True

            if updated:
                instance.updated_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"Instance {instance_id} mise à jour")

            return True

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'instance {instance_id}: {str(e)}")
            self.db.rollback()
            return False

    def delete_instance(self, instance_id: int) -> bool:
        """
        Supprime une instance.

        Args:
            instance_id: ID de l'instance à supprimer

        Returns:
            True en cas de succès
        """
        try:
            instance = self.get_instance(instance_id)
            if not instance:
                return False

            self.db.delete(instance)
            self.db.commit()
            logger.info(f"Instance {instance_id} supprimée")

            return True

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'instance {instance_id}: {str(e)}")
            self.db.rollback()
            return False

    def rotate_token(self, instance_id: int, new_password: str) -> bool:
        """
        Effectue une rotation du token d'une instance.

        Args:
            instance_id: ID de l'instance
            new_password: Nouveau mot de passe pour obtenir un nouveau token

        Returns:
            True en cas de succès
        """
        try:
            instance = self.get_instance(instance_id)
            if not instance:
                return False

            # Tenter de s'authentifier avec le nouveau mot de passe
            old_token = decrypt_token(instance.api_token)
            instance.base_url, instance.username, old_token

            new_token = self._authenticate_instance(instance.base_url, instance.username, new_password)
            if not new_token:
                logger.error(f"Impossible de renouveler le token pour l'instance {instance_id}")
                return False

            # Tester la validité et mettre à jour
            version, status = self._test_instance_connection(instance.base_url, new_token, instance.username)

            # Chiffrer le nouveau token
            encrypted_token = encrypt_token(new_token)

            # Mettre à jour l'instance
            instance.api_token = encrypted_token
            instance.version = version
            instance.status = status
            instance.updated_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"Token rotaté pour l'instance {instance_id}")

            return True

        except Exception as e:
            logger.error(f"Erreur lors de la rotation du token de l'instance {instance_id}: {str(e)}")
            self.db.rollback()
            return False

    def test_connection(self, instance_id: int) -> Dict[str, Any]:
        """
        Teste la connexion à une instance et met à jour son statut.

        Args:
            instance_id: ID de l'instance

        Returns:
            Dictionnaire avec les informations de test
        """
        instance = self.get_instance(instance_id)
        if not instance:
            return {"success": False, "error": "Instance non trouvée"}

        try:
            # Récupérer le token déchiffré
            token = decrypt_token(instance.api_token)

            # Tester la connexion
            version, status = self._test_instance_connection(instance.base_url, token, instance.username)

            # Mettre à jour l'instance
            instance.version = version
            instance.status = status
            instance.updated_at = datetime.utcnow()

            if status == "active":
                instance.last_error = None
                instance.last_error_at = None
            else:
                instance.last_error = "Erreur de connexion"
                instance.last_error_at = datetime.utcnow()

            self.db.commit()

            return {
                "success": status == "active",
                "version": version,
                "status": status,
                "last_sync": instance.last_sync.isoformat() if instance.last_sync else None
            }

        except Exception as e:
            logger.error(f"Erreur lors du test de connexion de l'instance {instance_id}: {str(e)}")

            # Mettre à jour avec l'erreur
            instance.status = "error"
            instance.last_error = str(e)
            instance.last_error_at = datetime.utcnow()
            self.db.commit()

            return {"success": False, "error": str(e)}

    def get_decrypted_token(self, instance_id: int) -> Optional[str]:
        """
        Récupère le token déchiffré d'une instance.

        Args:
            instance_id: ID de l'instance

        Returns:
            Token déchiffré ou None si introuvable
        """
        instance = self.get_instance(instance_id)
        if not instance:
            return None

        try:
            return decrypt_token(instance.api_token)
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement du token de l'instance {instance_id}: {str(e)}")
            return None

    def _authenticate_instance(self, base_url: str, username: str, password: str) -> Optional[str]:
        """
        Authentifie auprès d'une instance Audiobookshelf et retourne le token.

        Args:
            base_url: URL de base de l'instance
            username: Nom d'utilisateur
            password: Mot de passe

        Returns:
            Token JWT ou None en cas d'échec
        """
        try:
            auth_url = urljoin(base_url + "/", "login")
            response = requests.post(
                auth_url,
                json={"username": username, "password": password},
                timeout=30,
                verify=True  # Vérification SSL
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("user", {}).get("token")
            else:
                logger.warning(f"Échec d'authentification: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de l'authentification à {base_url}: {str(e)}")
            return None

    def _test_instance_connection(self, base_url: str, token: str, username: str) -> tuple:
        """
        Teste la connexion à une instance et retourne version et statut.

        Args:
            base_url: URL de base
            token: Token d'authentification
            username: Nom d'utilisateur pour les appels

        Returns:
            Tuple (version, status)
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}

            # Tester avec un appel simple (récupération des bibliothèques)
            test_url = urljoin(base_url + "/", "api/libraries")
            response = requests.get(test_url, headers=headers, timeout=30, verify=True)

            if response.status_code == 200:
                # Récupérer la version depuis un autre endpoint si disponible
                version = self._get_instance_version(base_url, headers)
                return version, "active"
            else:
                logger.warning(f"Erreur de connexion: HTTP {response.status_code}")
                return None, "error"

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau lors du test de connexion: {str(e)}")
            return None, "connection_error"
        except Exception as e:
            logger.error(f"Erreur générale lors du test de connexion: {str(e)}")
            return None, "unknown_error"

    def _get_instance_version(self, base_url: str, headers: Dict[str, str]) -> Optional[str]:
        """
        Récupère la version de l'instance Audiobookshelf.

        Args:
            base_url: URL de base
            headers: En-têtes avec autorisation

        Returns:
            Version de l'instance ou None
        """
        try:
            # Certains endpoints peuvent retourner la version
            status_url = urljoin(base_url + "/", "api/status")
            response = requests.get(status_url, headers=headers, timeout=10, verify=True)

            if response.status_code == 200:
                data = response.json()
                return data.get("version") or data.get("serverVersion")
            else:
                # Endpoint alternatif ou valeur par défaut
                return "unknown"

        except Exception:
            return "unknown"