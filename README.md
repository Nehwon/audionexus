# AudioNexus - Gestionnaire d'Audiothèques

[![Version](https://img.shields.io/badge/version-0.3.2--alpha-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/)
[![Docker](https://img.shields.io/badge/Docker-✓-blue.svg)](docker-compose.yml)
[![Frontend](https://img.shields.io/badge/Frontend-React%2FTypeScript-61DAFB.svg)](frontend/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009485.svg)](backend/)

## 📋 Description

AudioNexus est une plateforme complète pour gérer et administrer des collections audio à partir d'une interface unifiée. La solution offre des fonctionnalités avancées de traitement et de gestion des livres audio, avec une attention particulière portée à la sécurité et à l'expérience utilisateur. AudioNexus peut se connecter à des instances Audiobookshelf existantes pour une gestion centralisée.

## 🚀 Démarrage rapide

### Prérequis

- Docker et Docker Compose
- Node.js 18+ (pour le développement frontend)
- Python 3.11+ (pour le développement backend)

### Avec Docker (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/audionexus.git
cd audionexus

# Copier le fichier d'environnement d'exemple
cp .env.example .env

# Démarrer les services
docker compose up -d
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

### 🔐 Authentification & Sécurité
- ✅ Authentification JWT avec rafraîchissement de token
- ✅ Protection des routes avec authentification
- ✅ Gestion des sessions utilisateur
- 🔄 En cours : 2FA (Authentification à deux facteurs)
- 🔄 En cours : Réinitialisation de mot de passe

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
└── docs/                # Documentation
```

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
   ```

3. **Configuration**
   ```bash
   # Copier le fichier .env
   cp .env.example .env
   
   # Configurer les variables d'environnement
   nano .env
   ```

4. **Base de données**
   ```bash
   # Démarrer PostgreSQL avec Docker
   docker compose up -d db
   
   # Exécuter les migrations
   alembic upgrade head
   
   # Créer un superutilisateur
   python -m app.scripts.create_admin
   ```

5. **Lancer le serveur de développement**
   ```bash
   uvicorn app.main:app --reload
   ```

### Tests

```bash
# Lancer les tests
pytest

# Avec couverture de code
pytest --cov=app tests/

# Générer un rapport HTML
pytest --cov=app --cov-report=html tests/
open htmlcov/index.html  # Ouvrir le rapport
```

### Linting et formatage

```bash
# Vérifier le style de code
flake8 app/


# Formater le code
black app/


# Vérifier les types
mypy app/
```

## 📚 Documentation

La documentation est disponible dans le dossier `docs/` :

- [Guide d'installation](docs/installation.md)
- [Guide d'utilisation](docs/usage.md)
- [Documentation de l'API](docs/api.md)
- [Développement](docs/development.md)

Pour générer la documentation :

```bash
# Installer les dépendances de documentation
pip install -r docs/requirements.txt

# Générer la documentation
cd docs && make html

# Ouvrir la documentation générée
open _build/html/index.html
```

## 🤝 Contribution

1. **Fork** le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-nouvelle-fonctionnalite`)
3. Committez vos modifications (`git commit -am 'Ajout d\'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/ma-nouvelle-fonctionnalite`)
5. Créez une **Pull Request**

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📝 Changelog

Consultez le [CHANGELOG.md](CHANGELOG.md) pour suivre les modifications récentes.

## 📞 Contact

Pour toute question ou suggestion, veuillez ouvrir une [issue](https://github.com/votre-utilisateur/audiobooks-manager/issues).

---

<div align="center">
  <sub>Créé avec ❤️ par [Votre Nom]</sub>
</div>
   ```

3. Lancer l'application :
   ```bash
   uvicorn app.main:app --reload
   ```

### Production avec Docker

1. Construire et démarrer les conteneurs :
   ```bash
   docker-compose up -d --build
   ```

2. Vérifier les logs :
   ```bash
   docker-compose logs -f
   ```

3. Accéder à l'application :
   - Interface web : http://localhost:8000
   - Documentation API : http://localhost:8000/docs

## Gestion des données

### Sauvegardes

Pour sauvegarder la base de données :
```bash
docker-compose exec -T db pg_dump -U postgres audiobooks > backup_$(date +%Y%m%d).sql
```

### Restauration

Pour restaurer une sauvegarde :
```bash
cat backup_20230615.sql | docker-compose exec -T db psql -U postgres audiobooks
```

## Développement

### Technologies Utilisées

- Backend: Python (FastAPI)
- Frontend: Vue.js
- Base de données: PostgreSQL
- Moteur de recherche: Meilisearch
- Conteneurisation: Docker

### Contribution

1. Créer une branche pour votre fonctionnalité
2. Faire vos modifications
3. Soumettre une Pull Request

## Développement

### Configuration de l'environnement

1. Installer les dépendances de développement :
   ```bash
   pip install -e .[dev]
   ```

2. Configurer les hooks Git (optionnel) :
   ```bash
   pre-commit install
   ```

### Intégration Continue et Déploiement Continu (CI/CD)

Le projet utilise Gitea Actions pour le CI/CD. Le workflow comprend :

- **Tests** : Exécution des tests unitaires et d'intégration
- **Linting** : Vérification du style de code avec black, isort et flake8
- **Construction** : Création des images Docker et envoi vers le registre Gitea
- **Déploiement** : Déploiement automatique sur les environnements de staging et production

#### Branches

- `main` : Branche de production (déploiement automatique)
- `develop` : Branche de développement (déploiement en staging)
- `feature/*` : Branches de fonctionnalités (tests et linting uniquement)

#### Configuration requise

1. Activer les Actions dans les paramètres du dépôt Gitea
2. Configurer les secrets nécessaires (voir [.gitea/workflows/SECRETS.md](.gitea/workflows/SECRETS.md))
3. S'assurer que le registre de conteneurs est activé pour le dépôt

#### Secrets requis

Consultez le fichier [.gitea/workflows/SECRETS.md](.gitea/workflows/SECRETS.md) pour la liste complète des secrets nécessaires à la configuration du pipeline.

#### Exécution locale des tests

```bash
# Installer les dépendances de développement
pip install -e .[dev]

# Exécuter tous les tests
pytest

# Lancer le linting
black .
isort .
flake8 .
```

#### Construction locale de l'image Docker

```bash
docker build -t gitea.lamachere.fr/votre-utilisateur/audiobooks-manager:local .
```

### Tests

Lancer les tests unitaires :
```bash
pytest
```

### Formatage du code

Le code est formaté avec `black` et `isort` :
```bash
black .
isort .
```

## Licence

Ce projet est sous licence MIT.

## Contribution

1. Créer une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```

2. Faire un commit de vos modifications :
   ```bash
   git commit -m "Ajout: Nouvelle fonctionnalité"
   ```

3. Pousser les modifications :
   ```bash
   git push origin feature/nouvelle-fonctionnalite
   ```

4. Créer une Pull Request sur GitHub
