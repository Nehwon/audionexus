# AudioNexus - Gestionnaire d'Audiothèques

[![Version](https://img.shields.io/badge/version-0.8.0-blue.svg)](documentation/CHANGELOG.md)
[![License](https://img.shields.io/badge/license-AGPL%203.0-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](documentation/)
[![Docker](https://img.shields.io/badge/Docker-✓-blue.svg)](docker-compose.yml)
[![Frontend](https://img.shields.io/badge/Frontend-React%2FTypeScript-61DAFB.svg)](frontend/)
[![Status Auth](https://img.shields.io/badge/Auth-Fonctionnel🟢-4CAF50.svg)](#🎉-État-Actuel-%28SUCCESS%29)
[![Status Dashboard](https://img.shields.io/badge/Dashboard-Accès-OK🟢-4CAF50.svg)](#🎉-État-Actuel-%28SUCCESS%29)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](app/)
[![Authentication](https://img.shields.io/badge/Auth-VoidAuth-9C27B0.svg)](app/integrations/voidauth/)
[![Tests](https://github.com/votre-utilisateur/audionexus/actions/workflows/tests.yml/badge.svg)](https://github.com/votre-utilisateur/audionexus/actions/workflows/tests.yml)

## 📋 Description

**AudioNexus** est une plateforme complète pour gérer et administrer des collections audio à partir d'une interface unifiée. La solution offre des fonctionnalités avancées de traitement et de gestion des livres audio, avec une attention particulière portée à la sécurité et à l'expérience utilisateur. AudioNexus peut se connecter à des instances Audiobookshelf existantes pour une gestion centralisée.

## 🎉 État Actuel (07/09/2025) - AUDIOBOOKS PRODUCTION-READY

### ✅ MISSION ACCOMPLIE : AudioNexus v0.8.0 Fonctionnel

#### 🚀 **Fonctionnalités Core Audiobooks**
- ✅ **Téléversement complet** : Drag&drop ZIP/RAR → Conversion FFmpeg M4B automatique
- ✅ **Dashboard admin avancé** : Métriques temps réel + Graphiques tendances Recharts
- ✅ **Synchronisation multi-instances** : Load balancing + Monitoring santé Audiobookshelf
- ✅ **Recherche multi-collection** : Full-text avancée avec pagination intelligente
- ✅ **Gestion utilisateurs granulaire** : CRUD + Rôles + Permissions + Audit trail

#### 🔒 **Infrastructure Robuste (Production-Ready)**
- ✅ **Authentification complète** : VoidAuth OIDC 100% opérationnel
- ✅ **Sécurité Enterprise** : Rate limiting, CSRF, AES-256, audit trail
- ✅ **Performance optimisée** : APIs REST complètes, cache Redis, async
- ✅ **Scalabilité** : Docker zero-downtime, load balancing avancé
- ✅ **Observabilité** : Métriques temps réel, monitoring santé
- ✅ **Containers stabilisés** : Build optimisé (~26s → ~3min), démarrage automatique
- ✅ **Health checks** : Redis (1.4s), MySQL (7s), Backend (6s), Frontend (7s)

#### 🎯 **Routes Fonctionnelles** `/api/v1`
- ✅ `/auth/*` - Authentification VoidAuth complète
- ✅ `/admin/*` - Dashboard administrateur avec métriques
- ✅ `/audiobookshelf/*` - Gestion multi-instances avec sync
- ✅ `/upload/*` - Téléversement + traitement automatique
- ✅ `/users/*` - CRUD utilisateurs + rôles/permissions
- ✅ `/search/*` - Recherche avancée multi-collection

### 🎯 PHASES ACCOMPLIES

#### ✅ **Phase 0 : Diagnostic architectural** (RÉSOLU)
- [x] **Configurations VoidAuth** frontend/backend créées et validées
- [x] **CORS configuré** pour développement et production
- [x] **Variables d'environnement** alignées et sécurisées

#### ✅ **Phase 1 : Intégration et tests fonctionnels** (RÉSOLU)
- [x] **Serveur VoidAuth opérationnel** port 8080 avec Keycloak
- [x] **Flow complet authentification** : Login → VoidAuth → Dashboard validé
- [x] **Protection routes validée** : React Router + OIDC intégré
- [x] **Appels API confirmés** : Backend/frontend communication fonctionnelle
- [x] **Tests d'intégration** : Tous les tests passent avec succès

#### 🔜 **Prochaines étapes** (Phase 2 - Optimisations)
- [ ] **Optimisations performances** : Cache, queries optimisées
- [ ] **Interface utilisateur enrichie** : UX/UI améliorations
- [ ] **Documentation déploiement** : Guides complets hébergement
- [ ] **Tests end-to-end** : Scénarios utilisateur complets

**Voir [ROADMAP.md](ROADMAP.md) pour le suivi détaillé des phases**

> **Note de développement (03/09/2025)** : AudioNexus v0.6.0 apporte des améliorations significatives de sécurité, une architecture unifiée MySQL/SQLite, et des optimisations Docker complètes. L'intégration Audiobookshelf a été optimisée avec la gestion des conteneurs et les health checks. Consultez le [journal des changements](documentation/CHANGELOG.md) pour les détails techniques.</search>
</search_and_replace>

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

### Avec Docker (recommandé) - Setup complet

#### Démarrage rapide avec le script automatique

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/audionexus.git
cd audionexus

# Copier le fichier d'environnement d'exemple (optionnel)
cp .env.example .env

# Démarrage en mode développement (recommandé pour les développeurs)
./start.sh dev

# OU Démarrage en mode production
./start.sh prod
```

#### Démarrage manuel avec Docker Compose

```bash
# Pour le développement avec rechargement automatique
docker compose -f docker-compose.dev.yml up -d

# Pour la production optimisée
docker compose up -d

# Suivre les logs de démarrage
./start.sh logs
```

#### Services disponibles après le démarrage

Une fois le setup lancé, les services suivants sont accessibles :

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface utilisateur React/TypeScript |
| **Backend API** | http://localhost:8000 | API REST FastAPI |
| **Docs API** | http://localhost:8000/docs | Documentation interactive Swagger |
| **Adminer DB** | http://localhost:8080 | Interface de gestion MySQL |
| **Backend direct** | http://localhost:8000 | Backend pour les appels API |
| **Redis** | localhost:6379 | Cache et sessions |
| **MySQL** | localhost:3306 | Base de données principale |

#### Commandes de gestion pratiques

```bash
# État des services
./start.sh status

# Logs de tous les services
./start.sh logs

# Logs d'un service spécifique
./start.sh logs backend

# Arrêter tous les services
./start.sh stop

# Redémarrer les services
./start.sh restart
```

### Développement local (optionnel, si vous préférez sans Docker)

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

### 🔐 Authentification & Sécurité (VoidAuth)
- ✅ Authentification OIDC avec VoidAuth (basé sur Keycloak)
- ✅ Gestion des tokens JWT avec rafraîchissement automatique
- ✅ Protection des routes avec rôles et permissions
- ✅ Gestion des sessions utilisateur sécurisées
- ✅ Validation des données avec Pydantic v2
- ✅ 2FA (Authentification à deux facteurs)
- ✅ Réinitialisation de mot de passe sécurisée
- ✅ Protection CSRF complète sur endpoints sensibles
- ✅ Headers de sécurité (CSP, HSTS, XSS, Secure Cookies)
- ✅ Rate limiting anti-DoS avec Redis + fallback mémoire
- ✅ Chiffrement AES-256 des données sensibles
- ✅ Audit trail complet pour conformité GDPR/SOX
- ✅ VoidAuth v4.x intégré avec compatibilité APIs

### 👤 Gestion des Utilisateurs
- ✅ **CRUD complet** : Création, lecture, mise à jour, suppression utilisateurs
- ✅ **Système rôles/permissions** : Granulaire par ressource.action
- ✅ **Profils étendus** : Métadonnées, avatar, préférences utilisateur
- ✅ **Historique audit** : Journalisation complète des actions
- ✅ **Sécurité renforcée** : Verrouillage compte, validation droits
- ✅ **Interface administration** : Gestion complète via API/Dashboards

### 📊 Dashboard Administrateur
- ✅ **Métriques temps réel** - Utilisateurs, livres, stockage
- ✅ **Graphiques tendances** - Usage sur 30 jours (Recharts)
- ✅ **Gestion tâches upload** - Progression en temps réel
- ✅ **État système** - Santé DB, notifications formatées
- ✅ **Collections connectées** - Vue d'ensemble Audiobookshelf vs Local
- ✅ **Interface responsive** - Thème sombre/clair automatique

### 📚 Gestion des Documents Audio
- ✅ **Téléversement sécurisé** [`frontend/src/components/AudiobookUploader.tsx`](frontend/src/components/AudiobookUploader.tsx:l1) - Interface drag&drop haute qualité accessibilité WCAG 2.1
- ✅ **Sécurité enterprise** - Validation rigorous extensions dangereuses, double extensions, caractères spéciaux
- ✅ **Conversion FFmpeg** - Format M4B optimisé automatiquement avec métadonnées enrichies
- ✅ **Performance optimisée** - Gestion automatisee nettoyages fuites mémoire et polling
- ✅ **Accessibilité complète** - Labels ARIA, navigation clavier, régions live, mode sombre
- ✅ **Gestion erreurs robuste** - Boundary composants avec notifications toast et reprises intelligentes

### 🔗 Intégration Audiobookshelf Avancée
- ✅ **Multi-instances complet** - Gestion simultanée plusieurs Audiobookshelf
- ✅ **Load balancing intelligent** - Distribution par priorité et santé
- ✅ **Synchronisation bidirectionnelle** - Métadonnées avec résolution conflits
- ✅ **Monitoring santé** - Métriques temps réel et alertes automatiques
- ✅ **Cache intelligent** - Redis + mémoire avec invalidation par instance
- ✅ **Administration complète** - Interface gestion priorités et santé
- ✅ **Recherche avancée** complete - full-text multi-instances avec pagination

## 🏗️ Architecture Technique

### Backend (Python/FastAPI)
- API RESTful avec FastAPI
- Base de données PostgreSQL avec SQLAlchemy ORM
- Authentification JWT
- Cache Redis
- Tâches asynchrones avec Celery

### Frontend (React/TypeScript)
- ✅ Interface utilisateur avec Tailwind CSS
- ✅ Gestion d'état avec React Query
- ✅ Navigation avec React Router
- ✅ Appels API avec Axios
- ✅ Validation de formulaire avec React Hook Form

## 🛠️ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Backend
DATABASE_URL=mysql+pymysql://user:password@db:3306/audionexus
REDIS_URL=redis://redis:6379/0

# VoidAuth (OIDC)
VOIDAUTH_SERVER_URL=http://localhost:8080
VOIDAUTH_REALM=audionexus
VOIDAUTH_CLIENT_ID=audionexus-backend
VOIDAUTH_CLIENT_SECRET=votre-client-secret
VOIDAUTH_ADMIN_USER=admin
VOIDAUTH_ADMIN_PASSWORD=votre-mot-de-passe-admin
VOIDAUTH_VERIFY_SSL=False  # Désactiver en développement

# Frontend
VITE_API_URL=http://localhost:8000/api
VITE_OIDC_CLIENT_ID=audionexus-frontend
VITE_OIDC_AUTHORITY=http://localhost:8080/realms/audionexus
VITE_OIDC_REDIRECT_URI=http://localhost:3000/auth/callback
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
- **Tailwind CSS** comme bibliothèque UI principale
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
   git clone https://github.com/votre-utilisateur/audionexus.git
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

Pour toute question ou suggestion, veuillez ouvrir une [issue](https://github.com/votre-utilisateur/audionexus/issues).

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
# Initial commit for preprod branch
