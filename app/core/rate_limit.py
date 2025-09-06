"""
Module de configuration du rate limiting avec Redis pour la protection anti-DoS.
"""
import redis
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

logger = logging.getLogger(__name__)

def get_redis_connection():
    """
    Crée une connexion Redis pour le rate limiting.

    Returns:
        redis.Redis: Connexion Redis configurée avec gestion d'erreur
    """
    try:
        conn = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            password=settings.redis.password,
            socket_timeout=settings.redis.socket_timeout,
            socket_connect_timeout=settings.redis.socket_connect_timeout,
            socket_keepalive=settings.redis.socket_keepalive,
            socket_keepalive_options=settings.redis.socket_keepalive_options,
            decode_responses=True,
            retry_on_timeout=True,
            max_connections=20
        )
        # Test de la connexion
        conn.ping()
        logger.debug("Connexion Redis établie avec succès")
        return conn
    except redis.ConnectionError as e:
        logger.warning(f"Échec de connexion Redis: {str(e)} - passage en mode dégradé")
        # Retourne une connexion qui échouera gracieusement
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue Redis: {str(e)}", exc_info=True)
        return None

# Fonction de stockage adaptative pour Redis avec fallback
def get_storage_uri():
    """
    Retourne l'URI de stockage pour le rate limiting avec fallback sur mémoire.
    """
    try:
        # Test de connexion Redis
        conn = get_redis_connection()
        if conn:
            uri = f"redis://:{settings.redis.password or ''}@{settings.redis.host}:{settings.redis.port}/{settings.redis.db}"
            logger.info("Rate limiting: utilisation de Redis pour le stockage")
            return uri
        else:
            logger.warning("Rate limiting: Redis indisponible, utilisation de la mémoire locale")
            return "memory://"
    except Exception as e:
        logger.warning(f"Rate limiting: erreur Redis, fallback mémoire: {str(e)}")
        return "memory://"

# Configuration du limiter SlowAPI avec Redis et fallback
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=get_storage_uri(),
    strategy="fixed-window"
)

# Limites de taux par endpoint
RATE_LIMITS = {
    "auth": "10/minute",  # Authentification : 10 requêtes par minute
    "general": "100/minute",  # Requêtes générales : 100/minute
    "api": "200/minute",  # API générale : 200/minute
}