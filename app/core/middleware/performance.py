"""
Middleware FastAPI pour optimisations performance.

Fonctionnalités :
- Compression automatique GZip/Brotli des réponses
- Headers optimisés cache/ETags
- Logging requêtes lentes
- Rate limiting et throttling
- Monitoring temps réponse
"""

import gzip
import logging
import time
from typing import Callable, Optional, List
from collections import defaultdict

from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse

from app.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware de compression automatique des réponses API.

    Compresse automatiquement les réponses JSON volumineuses.
    Supporte GZip et Brotli selon préférence client.
    """

    def __init__(self, app, min_size: int = 1024):
        super().__init__(app)
        self.min_size = min_size  # Taille minimale pour compression
        self.supported_encodings = ["gzip", "br", "deflate"]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Récupérer préférences client
        accept_encoding = request.headers.get("accept-encoding", "")

        response = await call_next(request)

        # Ne pas compresser si réponse déjà compressée
        if response.headers.get("content-encoding"):
            return response

        # Compresser selon taille et type de contenu
        if self._should_compress(response, accept_encoding):
            encoding = self._get_preferred_encoding(accept_encoding)
            compressed_response = await self._compress_response(response, encoding)

            logger.debug(f"Compressed response: {encoding} ({len(response.body)} -> {len(compressed_response.body)} bytes)")
            return compressed_response

        return response

    def _should_compress(self, response: Response, accept_encoding: str) -> bool:
        """Détermine si la réponse doit être compressée."""
        # Vérifier taille minimale
        if hasattr(response, 'body') and len(response.body) < self.min_size:
            return False

        # Types de contenu à compresser
        compressible_types = [
            "application/json",
            "application/xml",
            "text/",
            "application/javascript"
        ]

        content_type = response.headers.get("content-type", "").lower()
        if not any(ct in content_type for ct in compressible_types):
            return False

        # Vérifier support client
        if not any(enc in accept_encoding for enc in self.supported_encodings):
            return False

        return True

    def _get_preferred_encoding(self, accept_encoding: str) -> str:
        """Détermine l'encodage préféré du client."""
        # Priorité: Brotli > GZip > Deflate
        if "br" in accept_encoding.split(","):
            return "br"
        elif "gzip" in accept_encoding.split(","):
            return "gzip"
        elif "deflate" in accept_encoding.split(","):
            return "deflate"

        return "gzip"  # Défaut

    async def _compress_response(self, response: Response, encoding: str) -> Response:
        """Compresse le contenu de la réponse."""
        if not hasattr(response, 'body'):
            return response

        try:
            if encoding == "gzip":
                compressed_data = gzip.compress(response.body, compresslevel=6)
            elif encoding == "br":
                # Brotli import dynamique (si disponible)
                try:
                    import brotli
                    compressed_data = brotli.compress(response.body, quality=6)
                except ImportError:
                    # Fallback GZip
                    compressed_data = gzip.compress(response.body, compresslevel=6)
                    encoding = "gzip"
            else:
                # Deflate (gzip compatible)
                compressed_data = gzip.compress(response.body, compresslevel=6)
                encoding = "gzip"

            # Créer nouvelle réponse compressée
            compressed_response = Response(
                content=compressed_data,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )

            # Ajouter headers compression
            compressed_response.headers["content-encoding"] = encoding
            compressed_response.headers["vary"] = "accept-encoding"

            return compressed_response

        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return response


class PerformanceMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware de monitoring performance des requêtes.

    Log les requêtes lentes et collecte métriques:
    - Temps de réponse
    - Taille réponse
    - Code HTTP
    - Endpoints lents (> seuil configurable)
    """

    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # secondes
        self.metrics = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "max_time": 0.0,
            "slow_count": 0,
            "errors": 0
        })

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Collecter métriques
            self._collect_metrics(request, response, duration)

            # Log requête lente
            if duration > self.slow_request_threshold:
                logger.warning(f"Slow request: {request.method} {request.url.path} "
                              ".2f")

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(".2f")
            raise

    def _collect_metrics(self, request: Request, response: Response, duration: float):
        """Collecte métriques détaillées."""
        endpoint = f"{request.method} {request.url.path}"

        with self.metrics[endpoint] as metric:
            metric["count"] += 1
            metric["total_time"] += duration
            metric["avg_time"] = metric["total_time"] / metric["count"]
            metric["max_time"] = max(metric["max_time"], duration)

            if duration > self.slow_request_threshold:
                metric["slow_count"] += 1

            if response.status_code >= 400:
                metric["errors"] += 1

    def get_metrics_report(self) -> dict:
        """Génère rapport métriques détaillé."""
        report = {
            "summary": {
                "total_endpoints": len(self.metrics),
                "slow_threshold_s": self.slow_request_threshold,
                "collected_at": time.time()
            },
            "endpoints": {}
        }

        for endpoint, metric in self.metrics.items():
            report["endpoints"][endpoint] = dict(metric)

        return report

    def get_slowest_endpoints(self, limit: int = 10) -> List[tuple]:
        """Retourne les endpoints les plus lents."""
        return sorted(
            self.metrics.items(),
            key=lambda x: x[1]["avg_time"],
            reverse=True
        )[:limit]


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour contrôle cache HTTP optimisé.

    Ajoute headers cache appropriés selon type de contenu:
    - Métriques : court TTL (30s)
    - Statiques : long TTL (1h)
    - API GET : moyen TTL (5min)
    - API POST/PUT/DELETE : no-cache
    """

    def __init__(self, app):
        super().__init__(app)

        # Stratégies cache par route pattern
        self.cache_policies = {
            # Cache court pour métriques fréquentes
            "*/dashboard/metrics": "public, max-age=30",
            "*/health": "public, max-age=60",

            # Cache moyen pour données utilisateur
            "*/users/*": "private, max-age=300",
            "*/instances/*": "private, max-age=300",

            # Pas de cache pour mutations
            "POST *": "no-cache",
            "PUT *": "no-cache",
            "DELETE *": "no-cache",

            # Cache avec revalidation pour fichiers
            "*/files/*": "private, max-age=3600, stale-while-revalidate=86400",
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Ne pas modifier headers cache existants
        if response.headers.get("cache-control"):
            return response

        # Déterminer stratégie cache
        cache_control = self._get_cache_control(request)

        if cache_control:
            response.headers["cache-control"] = cache_control

            # Ajouter ETag pour GET requests
            if request.method == "GET" and response.status_code == 200:
                if hasattr(response, 'body'):
                    import hashlib
                    etag = hashlib.md5(response.body).hexdigest()
                    response.headers["etag"] = f'"{etag}"'

        return response

    def _get_cache_control(self, request: Request) -> Optional[str]:
        """Détermine cache-control selon route et méthode."""
        method = request.method
        path = str(request.url.path)

        # Méthode spécifique
        method_pattern = f"{method} *"
        if method_pattern in self.cache_policies:
            return self.cache_policies[method_pattern]

        # Pattern path spécifique
        for pattern, policy in self.cache_policies.items():
            if "*" in pattern:
                # Pattern matching simple
                pattern_base = pattern.replace("*/", "").replace("/*", "")
                if pattern_base in path:
                    return policy

        # Défaut selon méthode
        if method in ["GET", "HEAD"]:
            return "private, max-age=60"  # Cache court par défaut
        else:
            return "no-cache"


class ThrottlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware de throttling simple basé sur adresse IP.

    Limite requêtes par IP pour prévention abuse.
    Utilise cache Redis pour persistence.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._cache_service = None

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = self._get_client_ip(request)

        if client_ip:
            allowed = await self._check_rate_limit(client_ip)

            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too many requests", "retry_after": 60}
                )

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extrait IP client depuis headers."""
        # X-Forwarded-For (load balancer/proxy)
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        # X-Real-IP (nginx)
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip

        # Remote addr fallback
        return getattr(request.client, 'host', None) if request.client else None

    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Vérifie limite taux pour IP donnée."""
        if not self._cache_service:
            from app.services.cache_service import CacheService
            self._cache_service = CacheService()

        key = f"ratelimit:{client_ip}"
        window_key = f"{key}:{int(time.time()) // 60}"  # Par minute

        try:
            # Récupérer compteur actuel
            current_count = await self._cache_service.get(window_key) or 0

            if current_count >= self.requests_per_minute:
                return False

            # Incrémenter compteur
            await self._cache_service.set(window_key, current_count + 1, 60)
            return True

        except Exception as e:
            logger.warning(f"Rate limit check failed for {client_ip}: {e}")
            return True  # Autoriser en cas d'erreur cache