# Guide de développement AudioNexus

Ce document fournit des instructions pour configurer un environnement de développement pour AudioNexus, la plateforme de gestion centralisée d'instances Audiobookshelf.

## 📋 Prérequis

- **Système d'exploitation** : Linux, macOS ou WSL2 (Windows)
- **Docker** : 20.10+
- **Docker Compose** : 2.0+
- **Node.js** : 18+ (pour le développement frontend)
- **Python** : 3.11+ (pour le développement backend)
- **Git** : 2.25+
- **npm** : 9.0+ ou **Yarn** : 1.22+

> 💡 Pour Windows, il est fortement recommandé d'utiliser WSL2 pour une meilleure expérience de développement.

## 🚀 Configuration de l'environnement

### 1. Cloner le dépôt

```bash
git clone https://gitea.lamachere.fr/fabrice/docker.git
cd docker/tools/audionexus
```

### 2. Configuration avec Docker (Recommandé)

#### Prérequis
- Assurez-vous que Docker et Docker Compose sont installés et en cours d'exécution
- Vérifiez que les ports 8000 (backend), 80/443 (Nginx) et 5432 (PostgreSQL) sont disponibles

#### Étapes d'installation

1. **Créer le fichier .env**
   ```bash
   cp .env.example .env
   ```
   > ⚠️ Modifiez les valeurs par défaut selon vos besoins, notamment les informations de base de données et les clés secrètes.

2. **Démarrer les services**
   ```bash
   docker compose up -d
   ```
   Cette commande va :
   - Construire les images nécessaires
   - Démarrer les conteneurs en arrière-plan
   - Configurer la base de données
   - Démarrer le serveur de développement

3. **Vérifier les logs**
   ```bash
   docker compose logs -f
   ```

### 3. Configuration du développement frontend

1. **Installer les dépendances**
   ```bash
   cd frontend
   npm install
   ```

2. **Démarrer le serveur de développement**
   ```bash
   npm run dev
   ```
   Le frontend sera disponible sur http://localhost:3000

### 4. Configuration du développement backend

#### Option 1 : Avec Docker (Recommandé)

1. **Accéder au conteneur**
   ```bash
   docker compose exec app bash
   ```

2. **Installer les dépendances**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Exécuter les migrations**
   ```bash
   alembic upgrade head
   ```

4. **Démarrer le serveur de développement**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Option 2 : En local

1. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

2. **Installer les dépendances**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Configurer la base de données**
   - Créer une base de données PostgreSQL nommée `audionexus`
   - Configurer les variables d'environnement dans `.env`
   - Exécuter les migrations : `alembic upgrade head`

4. **Démarrer le serveur**
   ```bash
   uvicorn app.main:app --reload
   ```

### 5. Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Application
APP_ENV=development
APP_SECRET=change_this_in_production
APP_DEBUG=true

# Base de données
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=audionexus
DB_HOST=db
DB_PORT=5432

# JWT
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (pour le développement)
FRONTEND_URL=http://localhost:3000

# Premier administrateur (sera créé au premier démarrage)
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=ChangeThisPassword
```
   
   # Configuration de l'application
   APP_ENV=development
   SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée
   
   # Configuration Audiobookshelf (optionnel pour le développement)
   ABS_HOST=http://localhost:13378
   ABS_USERNAME=admin@admin.com
   ABS_PASSWORD=password
   ```

3. Appliquer les migrations :
   ```bash
   alembic upgrade head
   ```

### 4. Configuration du frontend

1. Se déplacer dans le répertoire frontend :
   ```bash
   cd frontend
   ```

2. Installer les dépendances :
   ```bash
   npm install
   # ou
   yarn install
   ```

3. Copier le fichier d'environnement d'exemple :
   ```bash
   cp .env.example .env.local
   ```

   Puis éditez `.env.local` selon vos besoins.

## Exécution en mode développement

### Backend

```bash
# Dans le répertoire racine du projet
uvicorn app.main:app --reload
```

Le serveur sera disponible à l'adresse : http://localhost:8000

### Frontend

```bash
# Dans le répertoire frontend
npm run dev
# ou
yarn dev
```

L'application sera disponible à l'adresse : http://localhost:3000

## Structure du projet

```
audionexus/
├── alembic/             # Migrations de la base de données
├── app/                  # Code source du backend
│   ├── api/              # Points de terminaison API
│   ├── core/             # Configuration et logique métier
│   ├── db/               # Configuration de la base de données
│   ├── models/           # Modèles SQLAlchemy
│   └── schemas/          # Schémas Pydantic
├── frontend/             # Application frontend
│   ├── public/           # Fichiers statiques
│   └── src/              # Code source React
│       ├── components/   # Composants réutilisables
│       ├── pages/        # Composants de page
│       └── styles/       # Fichiers de style
├── tests/                # Tests automatisés
├── .env.example          # Exemple de fichier d'environnement
├── alembic.ini           # Configuration d'Alembic
├── pyproject.toml        # Configuration du projet Python
└── requirements.txt      # Dépendances Python
```

## Tests

### Backend

```bash
# Exécuter tous les tests
pytest

# Exécuter les tests avec couverture du code
pytest --cov=app --cov-report=term-missing
```

### Frontend

```bash
# Dans le répertoire frontend
npm test
# ou
yarn test
```

## Normes de code

### Python

- Respecter les conventions PEP 8
- Utiliser le formatage automatique avec Black
- Vérifier le style avec Flake8
- Taper le code avec MyPy

Commandes utiles :

```bash
# Formater le code
black .

# Vérifier le style
flake8
# Vérifier les types
mypy .
```

### JavaScript/TypeScript

- Suivre le style Airbnb
- Utiliser Prettier pour le formatage
- Vérifier le style avec ESLint

## Contribution

1. Créer une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```

2. Faire des commits atomiques avec des messages descriptifs :
   ```
   type(portée): description courte (50 caractères max)
   
   Description plus détaillée si nécessaire (72 caractères par ligne)
   ```

   Types de commit :
   - feat : nouvelle fonctionnalité
   - fix : correction de bug
   - docs : modifications de la documentation
   - style : formatage, point-virgule manquant, etc. (pas de changement de code)
   - refactor : refactorisation du code de production
   - test : ajout ou modification de tests
   - chore : mise à jour des tâches de construction, configuration du gestionnaire de paquets

3. Pousser la branche vers le dépôt distant :
   ```bash
   git push origin feature/nom-de-la-fonctionnalite
   ```

4. Créer une Pull Request sur Gitea

## Déploiement

Voir le fichier `DEPLOYMENT.md` pour les instructions de déploiement en production.

## Dépannage

### Problèmes courants

**Erreur de connexion à la base de données**
- Vérifiez que PostgreSQL est en cours d'exécution
- Vérifiez les identifiants dans le fichier `.env`
- Exécutez `alembic upgrade head` pour appliquer les migrations

**Erreurs de dépendances**
- Essayez de supprimer le répertoire `__pycache__` et le fichier `.pytest_cache`
- Réinstallez les dépendances avec `pip install -e ".[dev]"`

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
