# Procédure d'Initialisation d'AudioNexus

Ce document décrit les étapes pour configurer l'environnement de développement d'AudioNexus.

## Prérequis

- Système d'exploitation : Linux/macOS/Windows (WSL2 recommandé pour Windows)
- Docker 20.10+ et Docker Compose
- Git
- Python 3.9+
- Node.js 16+ et npm 8+
- Un client SMTP pour les emails (ou un service comme MailHog pour le développement)

## 1. Configuration Initiale

### 1.1. Clonage du Dépôt

```bash
git clone https://gitea.lamachere.fr/fabrice/AudioNexus.git
cd AudioNexus
```

### 1.2. Configuration de l'Environnement

1. Copiez le fichier d'exemple d'environnement :
   ```bash
   cp .env.example .env
   ```

2. Modifiez le fichier `.env` avec vos paramètres :
   ```env
   # Configuration de la base de données
   POSTGRES_USER=audionexus
   POSTGRES_PASSWORD=change_this_secure_password
   POSTGRES_DB=audionexus
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   
   # Configuration de l'application
   SECRET_KEY=change_this_to_a_secure_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   
   # Configuration CORS
   FRONTEND_URL=http://localhost:3000
   
   # Premier utilisateur administrateur
   FIRST_SUPERUSER_EMAIL=admin@example.com
   FIRST_SUPERUSER_PASSWORD=change_this_secure_password
   
   # Configuration SMTP (exemple avec MailHog pour le développement)
   SMTP_TLS=False
   SMTP_PORT=1025
   SMTP_HOST=mailhog
   SMTP_USER=
   SMTP_PASSWORD=
   EMAILS_FROM_EMAIL=noreply@audionexus.local
   ```

## 2. Démarrage des Services

### 2.1. Avec Docker Compose (Recommandé)

```bash
docker-compose up -d
```

Cela démarrera les services suivants :
- `backend` : L'API FastAPI
- `frontend` : L'application React (en mode développement)
- `db` : La base de données PostgreSQL
- `redis` : Le cache Redis
- `mailhog` : Un serveur SMTP de test
- `nginx` : Le serveur web Nginx (en mode développement)

### 2.2. Vérification des Services

Vérifiez que tous les services sont en cours d'exécution :

```bash
docker-compose ps
```

## 3. Configuration du Backend

### 3.1. Installation des Dépendances

```bash
docker-compose exec backend pip install -e ".[dev]"
```

### 3.2. Application des Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 3.3. Création de l'Utilisateur Administrateur

L'utilisateur administrateur est automatiquement créé au premier démarrage avec les identifiants spécifiés dans le fichier `.env`.

## 4. Configuration du Frontend

### 4.1. Installation des Dépendances

```bash
cd audionexus/frontend
npm install
```

### 4.2. Configuration de l'Environnement

Créez un fichier `.env` dans le dossier `audionexus/frontend` :

```env
VITE_API_URL=http://localhost:8000
# Autres variables d'environnement si nécessaire
```

### 4.3. Démarrage du Serveur de Développement

```bash
npm run dev
```

## 5. Accès à l'Application

- **Frontend** : http://localhost:3000
- **Backend (API)** : http://localhost:8000
- **Documentation de l'API** : http://localhost:8000/docs
- **MailHog (Emails de test)** : http://localhost:8025

## 6. Arrêt des Services

Pour arrêter tous les services :

```bash
docker-compose down
```

Pour supprimer également les volumes (attention, cela supprimera toutes les données) :

```bash
docker-compose down -v
```

## 7. Développement

### 7.1. Backend

- Le code source se trouve dans `audionexus/backend/app`
- Les tests s'exécutent avec :
  ```bash
  docker-compose exec backend pytest
  ```
- Pour appliquer de nouvelles migrations :
  ```bash
  docker-compose exec backend alembic revision --autogenerate -m "description des changements"
  docker-compose exec backend alembic upgrade head
  ```

### 7.2. Frontend

- Le code source se trouve dans `audionexus/frontend/src`
- Les tests s'exécutent avec :
  ```bash
  cd audionexus/frontend
  npm test
  ```
- Pour construire l'application pour la production :
  ```bash
  npm run build
  ```

## 8. Dépannage

### 8.1. Problèmes de Base de Données

Si la base de données ne démarre pas correctement :

```bash
docker-compose down -v
docker-compose up -d db
# Attendez que la base de données soit prête, puis :
docker-compose up -d
```

### 8.2. Problèmes de Dépendances

Si vous rencontrez des problèmes avec les dépendances :

```bash
docker-compose build --no-cache
```

### 8.3. Journalisation

Pour voir les logs des conteneurs :

```bash
docker-compose logs -f
```

## 9. Mise en Production

Pour une installation en production, consultez le guide de déploiement dans `docs/deployment/production.md`.

## 10. Support

Pour toute question ou problème, veuillez ouvrir une issue sur notre [dépôt Git](https://gitea.lamachere.fr/fabrice/AudioNexus/issues) ou contacter l'équipe de développement à l'adresse support@audionexus.fr.
