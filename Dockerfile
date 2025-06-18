# Étape de construction
FROM python:3.11-slim as builder

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY pyproject.toml .
RUN pip install --user -e .

# Étape d'exécution
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python installées
COPY --from=builder /root/.local /root/.local

# Ajouter le chemin des binaires Python au PATH
ENV PATH="/root/.local/bin:${PATH}"

# Créer les répertoires nécessaires
RUN mkdir -p /app/data/audionexus /app/data/config /app/data/database

# Copier le code source
COPY . .

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_ENV=production

# Port d'écoute de l'application
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
