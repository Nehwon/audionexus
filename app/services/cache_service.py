"""
Service de cache Redis/Redis-compatible pour optimiser les performances.

Fonctionnalités :
- Cache métriques dashboard fréquentes
- Cache requêtes coûteuses avec TTL
- Cache fichiers temporaires calculés
- Métriques performances cache
- Invalidation intelligente
- Fallback memory si Redis indisponible
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union, Callable
from contextlib import asynccontextmanager

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Statistiques du cache."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0
    memory_usage: Optional[int] = None

    @property
    def hit_ratio(self) -> float:
        """Taux de succès du cache."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


@dataclass
class CacheEntry:
    """Entrée de cache avec métadonnées."""
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: float = None
    accessed_at: float = None
    access_count: int = 0
    compressed: bool = False
    size_bytes: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class MemoryCache:
    """
    Cache en mémoire comme fallback si Redis n'est pas disponible.
    Utilise un LRU simple avec taille limitée.
    """

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._access_order: List[str] = []
        self.stats = CacheStats()

    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        if key in self._cache:
            entry = self._cache[key]

            # Vérifier expiration
            if entry.ttl and time.time() - entry.created_at > entry.ttl:
                # Supprimer entrée expirée
                self._cache.pop(key, None)
                if key in self._access_order:
                    self._access_order.remove(key)
                return None

            # Mettre à jour accès
            entry.accessed_at = time.time()
            entry.access_count += 1

            # Déplacer en tête d'accès
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

            self.stats.hits += 1
            return entry.value

        self.stats.misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stocke une valeur dans le cache."""
        # Serialize value pour calculer taille
        try:
            serialized = json.dumps(value)
            size_bytes = len(serialized.encode('utf-8'))
        except Exception:
            size_bytes = len(str(value).encode('utf-8'))

        # Vérifier limite taille
        if len(self._cache) >= self._max_size:
            # Évincer entrée la moins récemment utilisée
            if self._access_order:
                lru_key = self._access_order.pop(0)
                self._cache.pop(lru_key, None)
                self.stats.evictions += 1

        entry = CacheEntry(
            key=key,
            value=value,
            ttl=ttl,
            size_bytes=size_bytes
        )

        self._cache[key] = entry
        self.stats.sets += 1

        if key not in self._access_order:
            self._access_order.append(key)

        return True

    async def delete(self, key: str) -> bool:
        """Supprime une entrée du cache."""
        if key in self._cache:
            self._cache.pop(key, None)
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False

    async def clear(self) -> bool:
        """Vide complètement le cache."""
        self._cache.clear()
        self._access_order.clear()
        return True

    async def get_stats(self) -> CacheStats:
        """Récupère les statistiques du cache."""
        self.stats.memory_usage = sum(
            entry.size_bytes for entry in self._cache.values()
        )
        return self.stats

    async def close(self):
        """Ferme le cache (pas d'opération pour memory cache)."""
        pass


class RedisCache:
    """Cache utilisant Redis pour persistance et scalabilité."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis non disponible - utiliser MemoryCache")

        self.redis_url = redis_url
        self._client = None
        self.stats = CacheStats()

    async def _get_client(self):
        """Lazy initialization du client Redis."""
        if self._client is None:
            self._client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur depuis Redis."""
        try:
            client = await self._get_client()
            value_str = await client.get(key)

            if value_str is None:
                self.stats.misses += 1
                return None

            # Désérialiser
            try:
                value = json.loads(value_str)
            except json.JSONDecodeError:
                value = value_str

            self.stats.hits += 1
            return value

        except Exception as e:
            logger.warning(f"Erreur Redis get {key}: {e}")
            self.stats.misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stocke une valeur dans Redis."""
        try:
            client = await self._get_client()

            # Sérialiser
            try:
                value_str = json.dumps(value)
            except Exception:
                value_str = str(value)

            success = await client.set(key, value_str, ex=ttl)
            self.stats.sets += 1
            return bool(success)

        except Exception as e:
            logger.warning(f"Erreur Redis set {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Supprime une clé de Redis."""
        try:
            client = await self._get_client()
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Erreur Redis delete {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Vide complètement Redis."""
        try:
            client = await self._get_client()
            await client.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Erreur Redis clear: {e}")
            return False

    async def get_stats(self) -> CacheStats:
        """Récupère les statistiques Redis."""
        try:
            client = await self._get_client()
            redis_info = await client.info()

            self.stats.memory_usage = redis_info.get('used_memory', 0)
            return self.stats

        except Exception as e:
            logger.warning(f"Erreur récupération stats Redis: {e}")
            return self.stats

    async def close(self):
        """Ferme la connexion Redis."""
        if self._client:
            await self._client.close()
            self._client = None


class CacheService:
    """
    Service de cache unifié - Redis avec fallback memory.

    Utilise Redis pour persistence/scalabilité, memory comme fallback.
    Cache intelligent pour métriques dashboard et requêtes coûteuses.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL or "redis://localhost:6379/0"

        # Initialiser avec Redis si disponible, sinon memory
        if REDIS_AVAILABLE:
            try:
                self._cache = RedisCache(self.redis_url)
                self._cache_type = "redis"
            except Exception as e:
                logger.warning(f"Redis indisponible ({e}) - fallback memory")
                self._cache = MemoryCache()
                self._cache_type = "memory"
        else:
            logger.info("Redis non installé - utilisation memory cache")
            self._cache = MemoryCache()
            self._cache_type = "memory"

        # Clés de cache prédéfinies
        self.DASHBOARD_METRICS_KEY = "dashboard:metrics"
        self.USER_METRICS_PREFIX = "user:metrics:"
        self.INSTANCE_HEALTH_PREFIX = "instance:health:"
        self.FILE_STATS_PREFIX = "file:stats:"
        self.CONVERSION_CACHE_PREFIX = "conversion:"

        # TTL par défaut (secondes)
        self.DEFAULT_TTL = {
            'dashboard': 30,      # 30 secondes
            'user_metrics': 60,   # 1 minute
            'health': 300,        # 5 minutes
            'file_stats': 600,    # 10 minutes
            'conversion': 3600,   # 1 heure
            'system_info': 1800,  # 30 minutes
        }

    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        return await self._cache.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        category: str = "default"
    ) -> bool:
        """Stocke une valeur dans le cache avec TTL par catégorie."""
        if ttl is None:
            ttl = self.DEFAULT_TTL.get(category, 300)

        logger.debug(f"Cache SET {category}: {key} (TTL: {ttl}s)")
        return await self._cache.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """Supprime une clé du cache."""
        return await self._cache.delete(key)

    async def clear_category(self, category: str) -> int:
        """Vide toutes les clés d'une catégorie."""
        # Pour Redis, utiliser pattern matching
        if self._cache_type == "redis":
            try:
                delete_count = 0
                # Récupérer toutes les clés de la catégorie
                client = await self._cache._get_client()
                pattern = f"*:category" if category == "default" else f"{category}:*"

                cursor = 0
                while True:
                    cursor, keys = await client.scan(cursor, match=pattern, count=100)
                    if keys:
                        await client.delete(*keys)
                        delete_count += len(keys)
                    if cursor == 0:
                        break

                return delete_count
            except Exception:
                return 0
        else:
            # Pour memory cache, approche simplifiée
            return 0

    async def get_with_fallback(
        self,
        key: str,
        fallback_func: Callable,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ) -> Any:
        """
        Récupère avec fallback automatique.

        Args:
            key: Clé de cache
            fallback_func: Fonction appelée si pas en cache
            ttl: TTL pour le cache
            force_refresh: Forcer recalcul même si en cache

        Returns:
            Valeur (depuis cache ou calculée)
        """
        if not force_refresh:
            cached_value = await self.get(key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {key}")
                return cached_value

        logger.debug(f"Cache MISS: {key} - calculating...")
        computed_value = await fallback_func()

        # Cache la valeur calculée
        await self.set(key, computed_value, ttl)
        return computed_value

    # Méthodes spécifiques dashboard
    async def get_dashboard_metrics(self, force_refresh: bool = False):
        """Récupère métriques dashboard avec cache."""
        return await self.get_with_fallback(
            self.DASHBOARD_METRICS_KEY,
            self._compute_dashboard_metrics,
            self.DEFAULT_TTL['dashboard'],
            force_refresh
        )

    async def get_user_metrics(self, user_id: int, force_refresh: bool = False):
        """Récupère métriques utilisateur avec cache."""
        key = f"{self.USER_METRICS_PREFIX}{user_id}"
        return await self.get_with_fallback(
            key,
            lambda: self._compute_user_metrics(user_id),
            self.DEFAULT_TTL['user_metrics'],
            force_refresh
        )

    async def get_instance_health(self, instance_id: int):
        """Récupère santé instance avec cache."""
        key = f"{self.INSTANCE_HEALTH_PREFIX}{instance_id}"
        return await self.get(self.DASHBOARD_METRICS_KEY)  # Implémentation simplifiée

    # Méthodes de calcul (à implémenter selon les besoins)
    async def _compute_dashboard_metrics(self):
        """Calcule métriques dashboard coûteuses."""
        # Placeholder - à implémenter avec vraie logique
        return {
            "total_instances": 0,
            "active_instances": 0,
            "cached_at": time.time(),
            "computation_time": 0.001
        }

    async def _compute_user_metrics(self, user_id: int):
        """Calcule métriques utilisateur coûteuses."""
        # Placeholder
        return {
            "user_id": user_id,
            "upload_count": 0,
            "cached_at": time.time()
        }

    # Cache pour fichiers temporaires/conversion
    async def cache_conversion_result(self, task_id: str, result: Dict[str, Any]):
        """Cache résultat conversion pour récupération rapide."""
        key = f"{self.CONVERSION_CACHE_PREFIX}{task_id}"
        return await self.set(key, result, self.DEFAULT_TTL['conversion'], "conversion")

    async def get_conversion_result(self, task_id: str):
        """Récupère résultat conversion en cache."""
        key = f"{self.CONVERSION_CACHE_PREFIX}{task_id}"
        return await self.get(key)

    # Statistiques et monitoring
    async def get_stats(self) -> Dict[str, Any]:
        """Récupère statistiques complètes du cache."""
        cache_stats = await self._cache.get_stats()

        return {
            "cache_type": self._cache_type,
            "redis_url": self.redis_url if REDIS_AVAILABLE else None,
            "stats": asdict(cache_stats),
            "categories_ttl": self.DEFAULT_TTL,
            "uptime": time.time(),  # Timestamp pour uptime monitoring
        }

    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé du service cache."""
        try:
            # Test simple d'écriture/lecture
            test_key = "health_check"
            test_value = f"health_{time.time()}"

            success = await self.set(test_key, test_value, 60)
            if not success:
                raise Exception("Échec écriture cache")

            retrieved = await self.get(test_key)
            if retrieved != test_value:
                raise Exception("Échec lecture cache")

            # Cleanup
            await self.delete(test_key)

            return {
                "healthy": True,
                "cache_type": self._cache_type,
                "response_time_ms": 0,  # À mesurer réellement si besoin
                "checked_at": time.time()
            }

        except Exception as e:
            return {
                "healthy": False,
                "cache_type": self._cache_type,
                "error": str(e),
                "checked_at": time.time()
            }

    async def close(self):
        """Ferme proprement le service cache."""
        await self._cache.close()

    # Context manager support
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Instance globale pour utilisation dans l'application
_cache_instance = None

async def get_cache_service() -> CacheService:
    """Factory function pour service cache singleton."""
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = CacheService()

    return _cache_instance

# Pour utilisation synchrone lors du shutdown
def get_cache_service_sync():
    """Version synchrone pour shutdown cleanup."""
    global _cache_instance
    return _cache_instance

# Lifecycle functions pour intégration FastAPI
@asynccontextmanager
async def lifespan_cache(app):
    """Lifecycle manager pour cache service."""
    cache = await get_cache_service()
    yield
    await cache.close()