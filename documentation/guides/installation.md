# Guide d'Installation d'AudioNexus

Ce guide vous explique comment installer et configurer AudioNexus sur votre système.

## Prérequis

- Docker 20.10+ et Docker Compose
- Git
- Au moins 2 Go de RAM disponibles
- Au moins 10 Go d'espace disque libre

## Installation

### 1. Clonage du Dépôt

```bash
git clone https://gitea.lamachere.fr/fabrice/AudioNexus.git
cd AudioNexus
```

### 2. Configuration de l'Environnement

1. Copiez le fichier d'exemple d'environnement :
   ```bash
   cp .env.example .env
   ```

2. Modifiez le fichier `.env` selon vos besoins. Les paramètres importants sont :
   - `POSTGRES_PASSWORD` : Mot de passe pour la base de données PostgreSQL
   - `SECRET_KEY` : Clé secrète pour les JWT
   - `FIRST_SUPERUSER_EMAIL` : Email du premier administrateur
   - `FIRST_SUPERUSER_PASSWORD` : Mot de passe du premier administrateur

### 3. Démarrage des Services

```bash
docker-compose up -d
```

Cette commande va démarrer tous les services nécessaires :
- Backend (FastAPI)
- Frontend (React)
- Base de données (PostgreSQL)
- Cache (Redis)
- Serveur de messagerie de test (MailHog)
- Proxy inverse (Nginx)

### 4. Vérification de l'Installation

Vérifiez que tous les services sont en cours d'exécution :

```bash
docker-compose ps
```

### 5. Accès à l'Application

- **Frontend** : http://localhost:3000
- **Backend (API)** : http://localhost:8000
- **Documentation de l'API** : http://localhost:8000/docs
- **MailHog (Emails de test)** : http://localhost:8025

## Configuration Avancée

### Configuration du Domaine Personnalisé

Pour utiliser un domaine personnalisé avec HTTPS :

1. Modifiez le fichier `nginx/nginx.conf` pour mettre à jour le `server_name`
2. Installez Certbot et obtenez un certificat SSL
3. Configurez Nginx pour utiliser le certificat SSL

### Configuration du Stockage

Par défaut, les fichiers sont stockés localement dans le volume Docker. Pour utiliser un stockage externe :

1. Montez votre volume de stockage dans le conteneur
2. Mettez à jour les variables d'environnement liées au stockage dans `.env`

## Mise à Jour

## Déploiement Zero-Downtime (Production)

AudioNexus supporte le déploiement zero-downtime avec rollback automatique :

### Installation via Script Automatisé

```bash
# Configuration initiale
git clone https://gitea.lamachere.fr/fabrice/AudioNexus.git
cd AudioNexus
cp .env.example .env.production
# Éditez .env.production selon vos besoins

# Installation automatisée
./scripts/setup_env.sh --environment production

# Premier déploiement
./scripts/docker-deploy.sh deploy -e production --replicas 3
```

### Mise à Jour avec Rollback Automatique

```bash
# Mise à jour sécurisée
git pull origin main
./scripts/docker-deploy.sh deploy -e production -t v2.0.0

# En cas d'échec, rollback automatique :
./scripts/docker-deploy.sh rollback
```

### Configuration Load Balancing

Pour le déploiement multi-serveurs :

1. **Frontend Load Balancer** (Nginx):
```nginx
upstream audionexus_backend {
    server backend1:8000 weight=10;
    server backend2:8000 weight=10;
    server backend3:8000 weight=10;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://audionexus_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **Déploiement avec multiples réplicas**:
```bash
./scripts/docker-deploy.sh deploy --replicas 3 --environment production
```

### Monitoring Post-Déploiement

```bash
# Vérifier l'état du déploiement
./scripts/docker-deploy.sh status

# Surveiller les logs en temps réel
./scripts/docker-deploy.sh logs
```

## Migration VoidAuth v4.x

Si vous utilisez VoidAuth, assurez-vous de la compatibilité :

```bash
# Mise à jour des dépendances
pip install --upgrade python-keycloak>=5.7.0

# Test de compatibilité
python -c "import app.integrations.voidauth.client; print('VoidAuth v4.x compatible')"
```

### Configuration VoidAuth v4.x

Ajoutez ces variables à votre `.env.production` :

```env
# VoidAuth v4.x Configuration
VOIDAUTH_SERVER_URL=https://your-voidauth-server.com:8443
VOIDAUTH_REALM=audionexus
VOIDAUTH_CLIENT_ID=audionexus-frontend
VOIDAUTH_CLIENT_SECRET=your-updated-secret
VOIDAUTH_VERIFY_SSL=true
```

## Synchronisation Audiobookshelf Avancée

### Gestion des Conflits de Données

La nouvelle version supporte la résolution intelligente des conflits :

```python
# Exemple d'utilisation de l'API de synchronisation
POST /api/v1/audiobookshelf/sync/instances/{instance_id}/sync
{
    "full_sync": false,
    "conflict_strategy": "latest_wins"
}
```

### Instances Multiples avec Tokens Sécurisés

```python
# Rotation automatique des tokens
PUT /api/v1/audiobookshelf/instances/{instance_id}/rotate-token
{
    "password": "nouveau_mot_de_passe"
}
```

## Migration de Données

### Mise à Jour vers MySQL/PostgreSQL (recommandé)

```bash
# Export depuis SQLite
sqlite3 audionexus.db .dump > backup.sql

# Configuration MySQL
cp .env.example .env.mysql
# Éditez DB_TYPE=mysql et autres paramètres

# Migration
docker-compose -f docker-compose.mysql.yml run --rm backend alembic upgrade head
```

## Dépannage

### Problèmes de Démarrage

Si un service ne démarre pas :

```bash
docker-compose logs [nom_du_service]
```

### Réinitialisation de l'Environnement

Pour tout réinitialiser (attention, cela supprimera toutes les données) :

```bash
docker-compose down -v
docker-compose up -d
```

## Support

Pour toute question ou problème, veuillez consulter notre [documentation](https://gitea.lamachere.fr/fabrice/AudioNexus) ou ouvrir une [issue](https://gitea.lamachere.fr/fabrice/AudioNexus/issues).
