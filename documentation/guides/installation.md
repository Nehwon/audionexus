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

Pour mettre à jour vers une version plus récente :

```bash
git pull
docker-compose build --no-cache
docker-compose down
docker-compose up -d
docker-compose exec backend alembic upgrade head
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
