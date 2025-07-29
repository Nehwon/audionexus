# AudioNexus - Gestionnaire d'Audiothèques

[![Version](https://img.shields.io/badge/version-0.4.0--dev-blue.svg)](documentation/CHANGELOG.md)
[![License](https://img.shields.io/badge/license-AGPL%203.0-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](documentation/)
[![Docker](https://img.shields.io/badge/Docker-✓-blue.svg)](docker-compose.yml)
[![Frontend](https://img.shields.io/badge/Frontend-Svelte%2FTypeScript-FF3E00.svg)](frontend/)
[![Backend](https://img.shields.io/badge/Backend-Flask-000000.svg)](app/)
[![Tests](https://github.com/votre-utilisateur/audionexus/actions/workflows/tests.yml/badge.svg)](https://github.com/votre-utilisateur/audionexus/actions/workflows/tests.yml)

## 📋 Description

**AudioNexus** est une plateforme complète pour gérer et administrer des collections audio à partir d'une interface unifiée. La solution offre des fonctionnalités avancées de traitement et de gestion des livres audio, avec une attention particulière portée à la sécurité et à l'expérience utilisateur. AudioNexus peut se connecter à des instances Audiobookshelf existantes pour une gestion centralisée.

> **Note de développement (28/07/2025)** : Le projet a été migré vers Flask pour le backend et Svelte pour le frontend. L'authentification est gérée par VoidAuth pour une meilleure sécurité et une meilleure maintenabilité. Consultez le [journal des changements](documentation/CHANGELOG.md) pour plus de détails sur les dernières modifications.

## 📝 Auteur

- **Fabrice Lamachère** (fabrice@lamachere.fr) - Développeur principal
- Alias : Nehwon
- Licence : [AGPL-3.0+](LICENSE)

## 🚀 Démarrage rapide

### Prérequis

- Docker et Docker Compose
- Node.js 18+ (pour le développement frontend)
- Python 3.11+ (pour le développement backend)
- MySQL 8.0+ (base de données principale)
- Redis (pour les sessions et le cache)

### Avec Docker (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/audionexus.git
cd audionexus

# Copier le fichier d'environnement d'exemple
cp .env.example .env

# Modifier le fichier .env si nécessaire (voir la section Configuration)

# Démarrer les services
docker compose up -d

# Initialiser la base de données (exécuter après le premier démarrage)
docker compose exec backend flask db upgrade
```

### Développement local

#### Backend

```bash
# Se placer dans le dossier du backend
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate

# Installer les dépendances
pip install -e .

# Lancer le serveur de développement
uvicorn app.main:app --reload
```

#### Frontend

```bash
# Se placer dans le dossier du frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

## 🌟 Fonctionnalités

### 🔐 Authentification & Sécurité (En cours de stabilisation)
- ✅ Authentification JWT avec rafraîchissement de token
- ✅ Protection des routes avec authentification
- ✅ Gestion des sessions utilisateur asynchrones
- ✅ Validation des données avec Pydantic v2
- 🔄 En cours : Résolution des problèmes de dépendances circulaires
- 🔄 Planifié : 2FA (Authentification à deux facteurs)
- 🔄 Planifié : Réinitialisation de mot de passe

### 👤 Gestion des Utilisateurs
- ✅ Création et gestion des comptes
- ✅ Rôles et permissions
- 🔄 En cours : Profils utilisateurs

### 📊 Tableau de Bord
- ✅ Vue d'ensemble
- ✅ Statistiques d'utilisation
- 🔄 En cours : Widgets personnalisables

### 📚 Gestion des Bibliothèques
- 🔄 En cours : Connexion aux instances Audiobookshelf
- 🔄 En cours : Synchronisation des métadonnées
- 🔄 En cours : Gestion des collections

## 🏗️ Architecture Technique

### Backend (Python/FastAPI)
- API RESTful avec FastAPI
- Base de données PostgreSQL avec SQLAlchemy ORM
- Authentification JWT
- Cache Redis
- Tâches asynchrones avec Celery

### Frontend (React/TypeScript)
- Interface utilisateur avec Chakra UI
- Gestion d'état avec React Query
- Navigation avec React Router
- Appels API avec Axios
- Validation de formulaire avec React Hook Form

## 🛠️ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Backend
DATABASE_URL=postgresql://user:password@db:5432/audionexus
REDIS_URL=redis://redis:6379/0
SECRET_KEY=votre_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend
VITE_API_URL=http://localhost:8000/api
```

## 📦 Déploiement

### Production avec Docker

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## 📄 Documentation

- [Guide d'installation](DEVELOPMENT.md)
- [État du projet](ETAT_DU_PROJET.md)
- [Journal des changements](CHANGELOG.md)
- [Documentation technique](docs/)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📜 Licence

Distribué sous licence MIT. Voir `LICENSE` pour plus d'informations.

## 📞 Contact

Votre nom - [@votretwitter](https://twitter.com/votretwitter) - email@exemple.com

Lien du projet : [https://github.com/votre-utilisateur/audionexus](https://github.com/votre-utilisateur/audionexus)
- ✅ Téléchargement sécurisé
- ✅ Extraction des métadonnées
- ✅ Validation des formats
- 🔄 En cours : Conversion vers M4B
- 🔄 En cours : Analyse antivirus

### 🔄 Intégration Audiobookshelf
- ✅ Connexion aux instances
- 🔄 En cours : Synchronisation du contenu
- 🔄 En cours : Gestion multi-instances
- 🔄 En cours : Répartition de charge

## 🛠️ Architecture Technique

### Frontend (En développement)
- React.js avec TypeScript
- **Chakra UI** comme bibliothèque UI principale
  - Thèmes personnalisables
  - Composants accessibles
  - Mode sombre/clair
- Redux Toolkit pour la gestion d'état
- React Query pour les requêtes API
- React Hook Form pour la validation des formulaires
- i18n pour l'internationalisation

### Backend
- **Framework** : FastAPI (Python 3.10+)
- **Base de données** : PostgreSQL 14+
- **Cache** : Redis
- **File d'attente** : Celery
- **Stockage** : Système de fichiers local / S3
- **Synchronisation** : Service de synchronisation des utilisateurs
- **Tâches asynchrones** : Gestion des opérations en arrière-plan

### Sécurité & Synchronisation
- **Authentification** : JWT avec refresh tokens
- **Hachage** : bcrypt/Argon2 pour les mots de passe
- **Protection** : CSRF/XSS
- **Validation** : Stricte des entrées
- **Synchronisation** :
  - Mappage des rôles avec Audiobookshelf
  - Synchronisation bidirectionnelle
  - Gestion des conflits
  - Journalisation détaillée

## 🚀 Feuille de Route

### Version 0.3.0 (En cours)
- [x] Authentification de base
- [ ] Interface administrateur minimale
- [ ] Gestion des fichiers de base
- [ ] Connexion à Audiobookshelf

### Version 0.5.0 (Planifiée)
- [ ] Gestion avancée des utilisateurs
- [ ] Tableau de bord complet
- [ ] Traitement par lots
- [ ] Analyse antivirus

### Version 1.0.0 (Futur)
- [ ] Gestion multi-instances
- [ ] API complète
- [ ] Documentation utilisateur
- [ ] Intégration continue

## 📦 Installation

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 2 Go de RAM minimum (4+ recommandé)
- 10 Go d'espace disque

### Démarrage rapide

1. Cloner le dépôt :
   ```bash
   git clone https://gitea.lamachere.fr/fabrice/docker.git
   cd docker/tools/audiobooks
   ```

2. Configurer l'environnement :
   ```bash
   cp .env.example .env
   # Éditer les variables nécessaires
   nano .env
   ```

3. Démarrer les services :
   ```bash
   docker compose up -d --build
   ```

4. Accéder à l'application :
   - Interface web : http://localhost:8000
   - Documentation API : http://localhost:8000/docs
   - Interface Admin : http://localhost:8000/admin

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment procéder :

1. Forker le projet
2. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committer vos modifications (`git commit -am 'Ajouter une fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Contact

Pour toute question ou suggestion, veuillez ouvrir une [issue](https://gitea.lamachere.fr/fabrice/docker/issues).

---

<div align="center">
  <sub>Développé avec ❤️ par l'équipe AudioNexus</sub>
</div>

## 📋 Prérequis

### 🖥️ Matériel
- Serveur Linux avec accès SSH
- 2 Go RAM minimum (4+ GB recommandé)
- 10 GB d'espace disque minimum

### 📚 Logiciels
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.8+ (développement uniquement)
- Certificat SSL (Let's Encrypt recommandé)
- Compte administrateur Audiobookshelf

## 🚀 Installation

### 1. Cloner le dépôt
```bash
git clone [URL_DU_DEPOT] audiobooks-manager
cd audiobooks-manager
```

### 2. Configuration initiale
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer la configuration
nano .env  # ou votre éditeur préféré
```

### 3. Configuration requise
Modifiez les variables essentielles dans `.env` :

```env
# Application
DEBUG=False  # Production
SECRET_KEY=générer-une-clé-sécurisée

# Base de données
DB_HOST=db
DB_USER=postgres
DB_PASSWORD=changer-mot-de-passe
DB_NAME=audiobooks

# JWT
JWT_SECRET=autre-clé-sécurisée

# Audiobookshelf
ABS_API_URL=https://votre-serveur:13378/api
ABS_USERNAME=admin
ABS_PASSWORD=votre-mot-de-passe-secure
```

### 4. Démarrer avec Docker
```bash
docker compose up -d --build
```

### 5. Vérification
```bash
docker compose ps  # Vérifier l'état des conteneurs
docker compose logs -f  # Voir les logs
```

L'application sera disponible sur : `http://localhost:8000`

## 🐍 Utilisation de l'API

### Exemple de client Python
```python
from app.api.audiobookshelf import AudiobookshelfClient

# Initialisation
client = AudiobookshelfClient(
    base_url="https://votre-serveur:13378",
    username="admin",
    password="votre-mot-de-passe"
)

# Lister les bibliothèques
libraries = client.get_libraries()
print("📚 Bibliothèques :", [lib['name'] for lib in libraries])

# Livres récents
recent_books = client.get_recently_added(limit=3)
for book in recent_books:
    print(f"🎧 {book.get('title')} - {book.get('author')}")
```

### Exemples avancés
Voir le dossier `examples/` pour plus de cas d'utilisation :
- Gestion des utilisateurs
- Téléversement de livres
- Gestion des métadonnées
- Suivi des tâches

## 🐳 Démarrage rapide avec Docker

1. **Préparation**
   ```bash
   # Cloner le dépôt
   git clone [URL_DU_DEPOT] audiobooks-manager
   cd audiobooks-manager
   
   # Configuration
   cp .env.example .env
   nano .env  # Configurer les variables
   ```

2. **Démarrage**
   ```bash
   # Premier démarrage
   docker compose up -d --build
   
   # Arrêter les services
   docker compose down
   
   # Voir les logs
   docker compose logs -f
   ```

3. **Accès**
   - Interface web : http://localhost:8000
   - Documentation API : http://localhost:8000/docs
   - Interface Admin : http://localhost:8000/admin

## 📂 Structure du Projet

```
.
├── .env.example           # Configuration d'exemple
├── docker-compose.yml     # Configuration Docker Compose
├── Dockerfile            # Image de l'application
├── requirements.txt      # Dépendances Python
│
├── app/                 # Code source principal
│   ├── api/              # Points d'API
│   ├── core/             # Configuration de base
│   ├── db/               # Modèles de base de données
│   ├── models/           # Modèles Pydantic
│   ├── schemas/          # Schémas de validation
│   ├── services/         # Logique métier
│   └── main.py           # Point d'entrée FastAPI
│
├── nginx/              # Configuration Nginx
│   └── conf.d/
│       └── nginx.conf    # Configuration du serveur web
│
├── scripts/            # Scripts utilitaires
├── tests/               # Tests automatisés
└── documentation/       # Documentation complète
```

## 🗃️ Base de Données

AudioNexus utilise actuellement SQLite comme base de données par défaut pour le développement et les tests, offrant une configuration simplifiée et une meilleure expérience de développement.

### Configuration actuelle

- **Moteur de base de données** : SQLite
- **Fichier de données** : `./audionexus.db`
- **Outil ORM** : SQLAlchemy 2.0 avec support asynchrone
- **Gestion des migrations** : Alembic

### Gestion des migrations

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "Description des modifications"

# Appliquer les migrations
alembic upgrade head
```

> **Note** : Pour la production, une migration vers MySQL ou PostgreSQL est recommandée pour les déploiements à grande échelle. Consultez la documentation pour plus de détails sur la configuration des bases de données de production.

## 🛠️ Développement

### Configuration initiale

1. **Environnement virtuel**
   ```bash
   # Créer un environnement virtuel
   python -m venv venv
   
   # Activer (Linux/Mac)
   source venv/bin/activate
   
   # Activer (Windows)
   .\venv\Scripts\activate
   ```

2. **Installation des dépendances**
   ```bash
   # Installer les dépendances de développement
   pip install -r requirements-dev.txt
   
   # Installer en mode développement
   pip install -e .

3. **Configuration initiale**
   ```bash
   # Copier le fichier .env d'exemple
   cp .env.example .env
   
   # Modifier le fichier .env selon vos besoins
   # (assurez-vous que SQLite est configuré comme base de données par défaut)
   ```

4. **Initialisation de la base de données**
   ```bash
   # Créer les tables de la base de données
   python -m app.db.init_db
   
   # Appliquer les migrations
   alembic upgrade head
   ```

5. **Lancer le serveur de développement**
   ```bash
   uvicorn app.main:app --reload
   ```

## 🧪 Tests

### Exécution des tests

```bash
# Lancer tous les tests
pytest

# Lancer les tests avec couverture de code
pytest --cov=app tests/

# Générer un rapport HTML de couverture
pytest --cov=app --cov-report=html tests/

# Ouvrir le rapport de couverture (Linux/Mac)
open htmlcov/index.html

# Pour les tests spécifiques à l'authentification
pytest app/tests/test_auth.py -v
```

### Environnement de test

Les tests s'exécutent avec une base de données SQLite en mémoire par défaut. Assurez-vous que votre fichier `.env.test` est correctement configuré :

```env
# .env.test
DATABASE_URL=sqlite+aiosqlite:///:memory:
TESTING=true
```

## 🛠️ Qualité du code

### Linting et formatage

```bash
# Vérifier le style du code avec flake8
flake8 app/

# Formater automatiquement le code avec black
black app/

# Vérifier les types statiques avec mypy
mypy app/

# Vérifier les imports non utilisés et les erreurs de qualité
python -m pylint app/

# Vérifier la sécurité avec bandit (analyse de sécurité)
bandit -r app/
```

### Pré-commit

Un hook de pré-commit est configuré pour exécuter automatiquement les vérifications de qualité avant chaque commit :

1. Installez le hook :
   ```bash
   pre-commit install
   ```

2. Le hook exécutera automatiquement :
   - Black (formatage)
   - isort (organisation des imports)
   - flake8 (vérification de style)
   - mypy (vérification de types)

Pour exécuter manuellement les vérifications sur tous les fichiers :
```bash
pre-commit run --all-files
```

## 📚 Documentation

La documentation complète est organisée comme suit :

### Documentation utilisateur
- [Guide d'installation](documentation/INSTALLATION.md) - Comment installer et configurer AudioNexus
- [Guide de l'utilisateur](documentation/USER_GUIDE.md) - Comment utiliser l'application
- [FAQ](documentation/FAQ.md) - Questions fréquemment posées

### Documentation technique
- [Architecture technique](documentation/ARCHITECTURE.md) - Vue d'ensemble de l'architecture
- [Guide API](documentation/API.md) - Documentation de l'API REST
- [Modèle de données](documentation/DATA_MODEL.md) - Structure de la base de données
- [Journal des changements](CHANGELOG.md) - Historique des versions et changements

### Pour les contributeurs
- [Guide de contribution](documentation/CONTRIBUTING.md) - Comment contribuer au projet
- [Guide de développement](documentation/DEVELOPMENT.md) - Configuration de l'environnement de développement
- [Conventions de code](documentation/CODING_STANDARDS.md) - Standards et bonnes pratiques
- [Processus de versioning](documentation/VERSIONING.md) - Gestion des versions et des releases

## 🤝 Comment contribuer

Les contributions sont les bienvenues ! Voici comment procéder :

1. **Forker** le dépôt
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/ma-nouvelle-fonctionnalite`)
3. Committer vos modifications (`git commit -am 'Ajout d\'une nouvelle fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/ma-nouvelle-fonctionnalite`)
5. Créer une **Pull Request**

### Ressources pour les contributeurs

- [Code de conduite](documentation/contributing/CODE_OF_CONDUCT.md)
- [Guide de contribution](documentation/contributing/CONTRIBUTING.md)
- [Processus de développement](documentation/contributing/DEVELOPMENT.md)
- [Modèle de Pull Request](documentation/contributing/PULL_REQUEST_TEMPLATE.md)

## 📄 Licence

Ce projet est sous licence AGPL-3.0. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📝 Changelog

Consultez le [CHANGELOG.md](CHANGELOG.md) pour suivre les modifications récentes.

## 📞 Contact

Pour toute question ou suggestion, veuillez ouvrir une [issue](https://github.com/votre-utilisateur/audionexus/issues) ou contacter l'équipe de développement.

---

<div align="center">
  <sub>Créé avec ❤️ par Fabrice Lamachère (Nehwon)</sub>
</div>
## 🚀 Déploiement

### Déploiement avec Docker (recommandé)

```bash
# Construire les images
docker-compose build

# Démarrer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### Configuration requise

- Docker 20.10+
- Docker Compose 2.0+
- Au moins 2 Go de RAM disponibles
- Au moins 1 Go d'espace disque

### Variables d'environnement

Copiez le fichier `.env.example` vers `.env` et ajustez les paramètres selon vos besoins :

```bash
# Configuration de la base de données
DATABASE_URL=sqlite+aiosqlite:///./audionexus.db

# Configuration JWT
JWT_SECRET=votre-clé-sécurisée
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration de l'application
APP_ENV=development
DEBUG=true
SECRET_KEY=votre-clé-sécurisée

# Configuration CORS (pour le développement)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

## 🤖 Intégration Continue

Le projet utilise GitHub Actions pour l'intégration continue. Le workflow comprend :

- Exécution des tests unitaires et d'intégration
- Vérification du style de code avec black, isort et flake8
- Vérification des types avec mypy
- Construction des images Docker

### Exécution locale des tests

```bash
# Installer les dépendances de développement
pip install -e .[dev]

# Exécuter tous les tests
pytest

# Lancer le linting
black .
isort .
flake8 .

# Vérifier les types
mypy .
```

## 🌐 Navigation

- [Retour en haut du document](#audionexus---gestionnaire-daudiothèques)
- [Documentation complète](documentation/)
- [Journal des changements](CHANGELOG.md)
- [Licence](LICENSE)

---

<div align="center">
  <sub>Créé avec ❤️ par Fabrice Lamachère (Nehwon) | 2023-2025</sub>
</div>
