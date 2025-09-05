# Étape de compilation des dépendances (optimisé pour cache)
FROM python:3.11-alpine AS dependencies-builder

# Installer les dépendances système compilées
RUN apk add --no-cache build-base libmagic curl git \
    && mkdir -p /tmp/wheels

# Créer un utilisateur pour la construction
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser

WORKDIR /tmp/build

# Copier les exigences avec checksum pour optimiser le cache
COPY requirements*.txt ./

# Installer les dépendances dans un environnement virtuel
ENV PATH="/tmp/venv/bin:$PATH"
RUN python -m venv /tmp/venv \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --only-binary=all -r requirements.txt \
    && pip wheel --no-cache-dir --wheel-dir=/tmp/wheels -r requirements.txt

# Étape de développement séparée pour hot reload optimisé
FROM python:3.11-alpine AS development-builder
COPY --from=dependencies-builder /tmp/venv /tmp/venv
COPY --from=dependencies-builder /tmp/wheels /tmp/wheels
ENV PATH="/tmp/venv/bin:$PATH"

# Étape de production ultra-optimisée
FROM python:3.11-alpine AS production

# Installer uniquement les dépendances d'exécution (sans build tools)
RUN apk add --no-cache --virtual .runtime-deps \
    libmagic \
    ffmpeg \
    curl \
    libgcc \
    tzdata \
    && rm -rf /var/cache/apk/*

# Créer un utilisateur non-root pour la sécurité
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser

# Variables d'environnement optimisées pour les performances
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1 \
    FLASK_APP=wsgi:app \
    FLASK_ENV=production \
    PATH="/app/venv/bin:$PATH" \
    UVICORN_WORKERS=4 \
    GUNICORN_WORKERS=4 \
    GUNICORN_WORKER_TIMEOUT=30

# Créer les répertoires nécessaires avec les bonnes permissions
RUN mkdir -p /app/data/{audionexus/uploads,cache,logs} /tmp && \
    chown -R appuser:appuser /app /tmp

# Switcher vers l'utilisateur non-root
USER appuser

WORKDIR /app

# Copier l'environnement virtuel optimisé depuis l'étape de compilation
COPY --from=dependencies-builder --chown=appuser:appuser /tmp/venv /app/venv

# Copier le code source (optimisé pour les couches Docker)
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser wsgi.py gunicorn.conf.py ./

# Copier pyproject.toml pour les métadonnées
COPY --chown=appuser:appuser pyproject.toml ./

# Copier le code source optimisé pour le cache Docker
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser wsgi.py .
COPY --chown=appuser:appuser gunicorn.conf.py .

# Healthcheck avancé avec métriques
HEALTHCHECK --interval=45s --timeout=15s --start-period=10s --retries=3 \
    CMD ["curl", "-f", "http://localhost:8000/health"] || exit 1

# Exposition optimisée du port
EXPOSE 8000

# Commande de production avec optimisations de performance
CMD ["gunicorn", \
     "--config", "gunicorn.conf.py", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "wsgi:app"]

# Étape de développement optimisée pour le hot reload
FROM development-builder AS development

# Installer les outils de développement avec multi-stage
USER root
RUN apk add --no-cache git build-base \
    && rm -rf /var/cache/apk/*

# Installer les dépendances de développement
RUN pip install --no-cache-dir \
    watchdog \
    pytest-watch \
    pytest-asyncio \
    debugpy

# Configurer le répertoire de développement
RUN mkdir -p /app && chown -R appuser:appuser /app

USER appuser
WORKDIR /app

# Copier le code source pour le développement
COPY --chown=appuser:appuser . .

# Healthcheck simplifié pour le développement
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de développement avec debug optimisé
CMD ["python", "-m", "uvicorn", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload", \
     "--reload-delay", "0.1", \
     "--log-level", "debug", \
     "wsgi:app"]
