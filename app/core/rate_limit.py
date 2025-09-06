"""
Module de configuration du rate limiting avec Redis pour la protection anti-DoS.
"""
import redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

def get_redis_connection():
    """
    Crée une connexion Redis pour le rate limiting.

    Returns:
        redis.Redis: Connexion Redis configurée
    """
    return redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        password=settings.redis.password,
        socket_timeout=settings.redis.socket_timeout,
        socket_connect_timeout=settings.redis.socket_connect_timeout,
        socket_keepalive=settings.redis.socket_keepalive,
        socket_keepalive_options=settings.redis.socket_keepalive_options,
        decode_responses=True
    )

# Configuration du limiter SlowAPI avec Redis
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://:{settings.redis.password or ''}@{settings.redis.host}:{settings.redis.port}/{settings.redis.db}",
    strategy="fixed-window"
)

# Limites de taux par endpoint
RATE_LIMITS = {
    "auth": "10/minute",  # Authentification : 10 requêtes par minute
    "general": "100/minute",  # Requêtes générales : 100/minute
    "api": "200/minute",  # API générale : 200/minute
}