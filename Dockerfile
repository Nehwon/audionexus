# Étape de construction
FROM python:3.11-slim as builder

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --user -r requirements.txt

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
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=wsgi:app
ENV FLASK_ENV=production

# Créer les répertoires nécessaires
RUN mkdir -p /app/data/audionexus/uploads /app/data/config

# Copier le code source
COPY . .

# Port d'écoute de l'application
EXPOSE 8000

# Définir le répertoire de travail
WORKDIR /app

# Commande de démarrage avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "wsgi:app"]
