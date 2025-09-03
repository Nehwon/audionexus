# Étape de construction
FROM python:3.11-alpine AS builder

# Installer les dépendances de compilation
RUN apk add --no-cache \
    build-base \
    libmagic-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Créer un utilisateur pour la construction
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser

# Changer de propriétaire et travailler dans /app
RUN mkdir -p /app && chown appuser:appuser /app
USER appuser

WORKDIR /app

# Copier d'abord les exigences pour utiliser le cache Docker
COPY --chown=appuser:appuser requirements*.txt ./

# Installer les dépendances Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Étape d'exécution optimisée pour production
FROM python:3.11-alpine AS production

# Installer les dépendances système nécessaires
RUN apk add --no-cache \
    libmagic \
    ffmpeg \
    curl \
    libgcc \
    && rm -rf /var/cache/apk/*

# Créer un utilisateur non-root pour la sécurité
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser

# Définir PYTHONPATH et autres variables d'environnement essentielles
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=wsgi:app
ENV FLASK_ENV=production
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Créer les répertoires nécessaires avec les bonnes permissions
RUN mkdir -p /app/data/audionexus/uploads /app/data/config /app/logs && \
    chown -R appuser:appuser /app

# Changer pour l'utilisateur non-root
USER appuser

WORKDIR /app

# Copier les dépendances Python depuis l'étape de construction
COPY --from=builder --chown=appuser:appuser /home/appuser/.local /home/appuser/.local

# Copier pyproject.toml pour les métadonnées
COPY --chown=appuser:appuser pyproject.toml ./

# Copier le code source optimisé pour le cache Docker
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser wsgi.py .
COPY --chown=appuser:appuser gunicorn.conf.py .

# Healthcheck amélioré
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exposition du port
EXPOSE 8000

# Commande optimisée avec configuration Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]

# Étape de développement avec hot reload
FROM production AS development

# Revenir à root pour les installations de développement
USER root

# Installer les outils de développement (git pour pip install git+, etc.)
RUN apk add --no-cache \
    git \
    build-base \
    && rm -rf /var/cache/apk/*

# Installer les dépendances de développement
RUN pip install --user --no-cache-dir \
    watchdog \
    pytest-watch

# Revenir à l'utilisateur non-root
USER appuser

# Commande de développement avec hot reload (sera overridé dans docker-compose)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000", "--reload"]
