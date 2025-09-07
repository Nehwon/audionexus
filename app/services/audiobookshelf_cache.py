"""
Système de cache intelligent pour optimiser les appels API Audiobookshelf.

Ce service met en cache les réponses des API Audiobookshelf avec gestion
intelligente des TTL, invalidation et optimisation des requêtes.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrée de cache avec métadonnées."""

    key: str
    data: Any
    created_at: datetime
    ttl_seconds: int
    hits: int = 0
    instance_id: Optional[int] = None
    tags: Set[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = set()

    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl_seconds

    def get_remaining_ttl(self) -> int:
        """Retourne le TTL restant en secondes."""
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return max(0, int(self.ttl_seconds - elapsed))


class AudiobookshelfCache:
    """Cache intelligent pour les API Audiobookshelf."""

    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 300):
        """Initialise le système de cache."""
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.redis_client = None
        self._lock = asyncio.Lock()

        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info("Cache Redis initialisé")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation Redis: {str(e)}")
                self.redis_client = None
        else:
            logger.info("Cache mémoire seulement (Redis non disponible)")

    async def get(self, key: str, instance_id: Optional[int] = None) -> Optional[Any]:
        """
        Récupère une valeur du cache.

        Args:
            key: Clé de cache
            instance_id: ID de l'instance (optionnel)

        Returns:
            Valeur cachée ou None
        """
        async with self._lock:
            # Essayer Redis d'abord si disponible
            if self.redis_client:
                try:
                    redis_key = self._make_redis_key(key, instance_id)
                    cached_data = await self.redis_client.get(redis_key)
                    if cached_data:
                        # Désérialiser et vérifier l'expiration
                        entry_data = json.loads(cached_data)
                        created_at = datetime.fromisoformat(entry_data["created_at"])

                        if not self._is_expired(
                            created_at, entry_data.get("ttl_seconds", self.default_ttl)
                        ):
                            await self._increment_hit_count(redis_key)
                            return entry_data["data"]

                        # Supprimer l'entrée expirée
                        await self.redis_client.delete(redis_key)

                except Exception as e:
                    logger.error(f"Erreur Redis: {str(e)}")

            # Fallback vers le cache mémoire
            entry = self.memory_cache.get(key)
            if entry and not entry.is_expired():
                entry.hits += 1
                return entry.data
            elif entry and entry.is_expired():
                # Supprimer l'entrée expirée
                del self.memory_cache[key]

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        instance_id: Optional[int] = None,
        tags: Optional[Set[str]] = None,
    ) -> bool:
        """
        Stocke une valeur dans le cache.

        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl_seconds: TTL en secondes (défaut: default_ttl)
            instance_id: ID de l'instance (optionnel)
            tags: Tags pour l'invalidation (optionnel)

        Returns:
            True si stocké avec succès
        """
        async with self._lock:
            ttl = ttl_seconds or self.default_ttl
            entry = CacheEntry(
                key=key,
                data=value,
                created_at=datetime.utcnow(),
                ttl_seconds=ttl,
                instance_id=instance_id,
                tags=tags or set(),
            )

            # Stocker dans Redis si disponible
            if self.redis_client:
                try:
                    redis_key = self._make_redis_key(key, instance_id)
                    entry_data = {
                        "data": value,
                        "created_at": entry.created_at.isoformat(),
                        "ttl_seconds": ttl,
                        "hits": 0,
                        "instance_id": instance_id,
                        "tags": list(tags) if tags else [],
                    }

                    success = await self.redis_client.setex(
                        redis_key, ttl, json.dumps(entry_data)
                    )

                    if success:
                        return True

                except Exception as e:
                    logger.error(f"Erreur Redis set: {str(e)}")

            # Fallback vers le cache mémoire
            self.memory_cache[key] = entry
            return True

    async def delete(self, key: str, instance_id: Optional[int] = None) -> bool:
        """
        Supprime une entrée du cache.

        Args:
            key: Clé à supprimer
            instance_id: ID de l'instance (optionnel)

        Returns:
            True si supprimé
        """
        async with self._lock:
            deleted = False

            # Supprimer de Redis
            if self.redis_client:
                try:
                    redis_key = self._make_redis_key(key, instance_id)
                    await self.redis_client.delete(redis_key)
                    deleted = True
                except Exception as e:
                    logger.error(f"Erreur Redis delete: {str(e)}")

            # Supprimer du cache mémoire
            if key in self.memory_cache:
                del self.memory_cache[key]
                deleted = True

            return deleted

    async def invalidate_by_tags(self, tags: Set[str]) -> int:
        """
        Invalide toutes les entrées ayant certains tags.

        Args:
            tags: Set de tags à invalider

        Returns:
            Nombre d'entrées invalidées
        """
        async with self._lock:
            invalidated = 0

            # Invalidation Redis
            if self.redis_client:
                try:
                    # Récupérer toutes les clés avec les tags spécifiés
                    # Note: Cela nécessiterait une implémentation plus complexe avec des sets Redis
                    # Pour simplifier, on invalide par pattern
                    for tag in tags:
                        pattern = f"*tag:{tag}*"
                        keys = await self.redis_client.keys(pattern)
                        if keys:
                            await self.redis_client.delete(*keys)
                            invalidated += len(keys)
                except Exception as e:
                    logger.error(f"Erreur Redis invalidation: {str(e)}")

            # Invalidation mémoire
            keys_to_remove = []
            for key, entry in self.memory_cache.items():
                if tags.intersection(entry.tags):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.memory_cache[key]
                invalidated += 1

            logger.info(f"Invalidé {invalidated} entrées avec tags: {tags}")
            return invalidated

    async def invalidate_by_instance(self, instance_id: int) -> int:
        """
        Invalide toutes les entrées d'une instance spécifique.

        Args:
            instance_id: ID de l'instance

        Returns:
            Nombre d'entrées invalidées
        """
        async with self._lock:
            invalidated = 0

            # Invalidation Redis
            if self.redis_client:
                try:
                    pattern = f"audiobookshelf:instance:{instance_id}:*"
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
                        invalidated += len(keys)
                except Exception as e:
                    logger.error(f"Erreur Redis invalidation instance: {str(e)}")

            # Invalidation mémoire
            keys_to_remove = []
            for key, entry in self.memory_cache.items():
                if entry.instance_id == instance_id:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.memory_cache[key]
                invalidated += 1

            logger.info(f"Invalidé {invalidated} entrées pour l'instance {instance_id}")
            return invalidated

    async def clear_all(self) -> int:
        """
        Vide complètement le cache.

        Returns:
            Nombre d'entrées supprimées
        """
        async with self._lock:
            cleared = 0

            # Clear Redis
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys("audiobookshelf:*")
                    if keys:
                        await self.redis_client.delete(*keys)
                        cleared += len(keys)
                except Exception as e:
                    logger.error(f"Erreur Redis clear: {str(e)}")

            # Clear mémoire
            cleared += len(self.memory_cache)
            self.memory_cache.clear()

            logger.info(f"Cache vidé: {cleared} entrées supprimées")
            return cleared

    def get_cache_stats(self) -> Dict:
        """
        Retourne les statistiques du cache.

        Returns:
            Dict avec les statistiques
        """
        memory_entries = len(self.memory_cache)
        memory_size = sum(len(str(entry.data)) for entry in self.memory_cache.values())
        total_hits = sum(entry.hits for entry in self.memory_cache.values())

        return {
            "memory_entries": memory_entries,
            "memory_size_bytes": memory_size,
            "total_hits": total_hits,
            "redis_available": self.redis_client is not None,
            "default_ttl": self.default_ttl,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _make_redis_key(self, key: str, instance_id: Optional[int] = None) -> str:
        """Crée une clé Redis avec préfixe."""
        if instance_id:
            return f"audiobookshelf:instance:{instance_id}:{key}"
        else:
            return f"audiobookshelf:global:{key}"

    def _is_expired(self, created_at: datetime, ttl_seconds: int) -> bool:
        """Vérifie si une entrée est expirée."""
        return (datetime.utcnow() - created_at).total_seconds() > ttl_seconds

    async def _increment_hit_count(self, redis_key: str):
        """Incrémente le compteur de hits dans Redis (optionnel)."""
        if self.redis_client:
            try:
                # On pourrait implémenter un compteur de hits ici
                pass
            except Exception:
                pass

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.redis_client:
            await self.redis_client.close()

    # Méthodes utilitaires pour les clés de cache courantes

    def make_library_key(self, instance_id: int, library_id: str) -> str:
        """Crée une clé pour une bibliothèque."""
        return f"library:{library_id}"

    def make_audiobook_key(self, instance_id: int, audiobook_id: str) -> str:
        """Crée une clé pour un audiobook."""
        return f"audiobook:{audiobook_id}"

    def make_progress_key(
        self, instance_id: int, user_id: str, audiobook_id: str
    ) -> str:
        """Crée une clé pour la progression d'un utilisateur."""
        return f"progress:{user_id}:{audiobook_id}"

    async def warmup_cache(self, instance_id: int):
        """
        Précharge le cache avec les données les plus fréquemment utilisées.

        Args:
            instance_id: ID de l'instance à précharger
        """
        logger.info(f"Préchargement du cache pour l'instance {instance_id}")
        # Implémentation du warmup selon les besoins
        # Par exemple: charger les bibliothèques, utilisateurs fréquents, etc.
        pass
