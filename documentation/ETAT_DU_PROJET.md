# État du Projet AudioNexus - 20/07/2025

## 📌 Vue d'ensemble
AudioNexus est une plateforme complète pour gérer et administrer plusieurs instances de bibliothèques audio à partir d'une interface unifiée. Le projet vise à simplifier la gestion des bibliothèques d'audiobooks avec des fonctionnalités avancées de traitement et de gestion.

## ⚠️ État actuel (21/07/2025)
- **Dernière action** : Correction des erreurs d'authentification
- **Statut** : Développement actif - Correction des tests
- **Branche** : `fix/authentication-issues`
- **Problèmes critiques** : 
  - Erreur 500 dans l'endpoint `/auth/register`
  - Problème de validation Pydantic v2 avec `UserCreate`
  - Gestion des sessions asynchrones à finaliser
- **Tâches en cours** :
  - Migration complète vers MySQL
  - Correction des tests d'authentification
  - Unification de la gestion des sessions

## 📊 Version actuelle
- **Version** : 0.3.5-alpha (en développement actif)
- **Dernière mise à jour** : 20/07/2025
- **Statut** : Développement actif - Migration vers MySQL
- **Branche** : `feature/mysql-migration`
- **Environnement** : Développement local avec Docker (MySQL)

## 🏗️ Architecture Technique

### Backend (Python/FastAPI)
- ✅ API RESTful avec FastAPI
- 🟡 Migration de PostgreSQL vers MySQL avec SQLAlchemy ORM (en cours)
  - ✅ Ajout du service MySQL dans docker-compose
  - ✅ Création du script d'initialisation SQL
  - ✅ Configuration des connexions SQLAlchemy
  - ⏳ Adaptation des modèles et requêtes
- ✅ Authentification JWT avec refresh tokens
- ✅ Migration vers Pydantic V2
  - ✅ Mise à jour des validateurs (@validator → @field_validator)
  - ✅ Adaptation des classes de configuration
  - ✅ Correction des avertissements de dépréciation
- ✅ Configuration Docker
  - ✅ Services conteneurisés avec MySQL
  - ✅ Dépendances entre services résolues
  - ✅ Configuration des volumes persistants pour MySQL
  - ✅ Correction des chemins d'importation
  - ✅ Mise à jour des dépendances Python (pymysql, asyncpg)
- 🔄 Gestion des sessions (en cours)
  - ✅ Création d'un gestionnaire unifié de sessions
  - ✅ Migration des dépendances vers le gestionnaire unifié
  - ⏳ Correction des problèmes de sessions sync/async

### Frontend (React/TypeScript)
- ✅ Structure de base du projet avec Vite + React + TypeScript
- ✅ Interface utilisateur avec **Chakra UI**
  - ✅ Configuration du thème personnalisable
  - ✅ Composants accessibles
  - ✅ Support du mode sombre/clair
  - ✅ Design System unifié
  - ✅ Navigation fluide avec React Router
- ✅ Pages principales
  - ✅ Page de connexion sécurisée
  - ✅ Tableau de bord administrateur
  - ✅ Gestion des utilisateurs
  - ✅ Page des paramètres
  - ✅ Page 404 personnalisée
- ✅ Gestion d'état avec Context API et React Query
- ✅ Appels API avec Axios et intercepteurs
- ✅ Protection des routes avec authentification
- ✅ Gestion des tokens JWT avec rafraîchissement automatique

### Infrastructure
- ✅ Configuration Docker avec services conteneurisés
  - ✅ Backend FastAPI
  - ✅ Base de données PostgreSQL

## 🎯 Prochaines étapes

### Priorité haute (Blocages critiques)
- [ ] Corriger la configuration des tests
  - [ ] Forcer l'utilisation de SQLite in-memory pour les tests
  - [ ] Isoler la configuration de test de la configuration de développement
  - [ ] Nettoyer les variables d'environnement système problématiques

- [ ] Résoudre les erreurs 500/422 dans les tests d'authentification
  - [ ] Auditer la génération des tokens JWT
  - [ ] Vérifier les en-têtes OAuth2
  - [ ] Valider la configuration des routes protégées

### Priorité moyenne (Améliorations en cours)
- [ ] Finaliser la migration vers MySQL
  - [ ] Adapter la configuration des moteurs SQLAlchemy
  - [ ] Tester les requêtes spécifiques à MySQL
  - [ ] Mettre à jour la documentation de déploiement

- [ ] Unifier la gestion des sessions
  - [ ] Supprimer les implémentations redondantes de get_db
  - [ ] Documenter l'utilisation du gestionnaire unifié
  - [ ] Mettre à jour les tests pour utiliser la nouvelle API

### Documentation
- [ ] Mettre à jour la documentation technique
  - [ ] Configuration requise
  - [ ] Guide de démarrage rapide
  - [ ] Dépannage des problèmes courants

### Prochain sprint
- [ ] Tests d'intégration
- [ ] Mise en place des pipelines CI/CD
- [ ] Documentation technique complète

## Notes techniques
- **Version Python** : 3.11+
- **Version Node.js** : 18+
- **Base de données** : MySQL 8
- **Cache** : Redis 7
- **Frontend** : React 18, TypeScript 5, Chakra UI
- **Backend** : FastAPI, SQLAlchemy 2.0, Pydantic v2

## 🚧 Problèmes connus et blocages

### Configuration et Variables d'environnement
- ⚠️ Variable `ACCESS_TOKEN_EXPIRE_MINUTES` corrompue (contient un commentaire)
  - Impact : Empêche la validation Pydantic
  - Solution : Nettoyer ou supprimer la variable système

### Base de données
- ⚠️ Conflit de configuration entre SQLite (tests) et MySQL (prod)
  - Impact : Les tests tentent de se connecter à PostgreSQL/MySQL au lieu de SQLite
  - Solution : Isoler la configuration de test

### Tests
- ⚠️ Erreurs 500/422 dans les tests d'authentification
  - Causes possibles : 
    - Gestion incohérente des sessions sync/async
    - Problèmes de configuration des dépendances
    - Conflits entre différentes implémentations de get_db

### Dépendances
- ⚠️ Multiples implémentations de get_db détectées
  - Fichiers concernés :
    - core/deps.py
    - db/database.py 
    - db/session.py
    - api/deps.py
    - core/dependencies.py

2. **Documentation**
   - Mise à jour en cours de la documentation technique
   - Guide d'installation à compléter

## Structure du projet
```
audionexus/
├── backend/            # Code source du backend
│   ├── app/            # Application FastAPI
│   ├── tests/          # Tests unitaires et d'intégration
│   └── alembic/        # Migrations de base de données
├── frontend/           # Application React/TypeScript
│   ├── public/         # Fichiers statiques
│   └── src/            # Code source du frontend
├── docker/             # Configuration Docker
│   ├── nginx/          # Configuration Nginx
│   └── db/             # Scripts d'initialisation de la base de données
├── docs/               # Documentation technique
└── scripts/            # Scripts utilitaires
```

## 🔗 Liens utiles
- [Documentation technique](docs/)
- [Guide d'installation](DEVELOPMENT.md)
- [Journal des changements](CHANGELOG.md)
- [Journal de développement](../developpement.md)

### Infrastructure
- ✅ Conteneurisation avec Docker
- ✅ Configuration via variables d'environnement
- ✅ Configuration Nginx pour le développement local
- ✅ Services conteneurisés :
  - ✅ Backend FastAPI
  - ✅ Base de données PostgreSQL
  - ✅ Cache Redis
  - ✅ Serveur Nginx
- 🔄 En cours : Configuration CI/CD
- 🔄 En cours : Tests automatisés
- 🔄 En cours : Configuration SSL pour la production

## Fonctionnalités Implémentées

### Authentification & Sécurité
- ✅ Authentification de base
- ✅ Chiffrement des mots de passe (bcrypt/Argon2)
- ✅ Gestion des sessions JWT avec refresh tokens
- ✅ Protection des routes API
- ✅ Architecture de synchronisation des utilisateurs

### Gestion des Utilisateurs
- ✅ Authentification unifiée
- ✅ Modèle de données pour la synchronisation
- 🔄 En cours : Moteur de synchronisation
- 🔄 En cours : Gestion des conflits

### Gestion des Fichiers
- ✅ Téléchargement de base
- ✅ Validation des types de fichiers
- 🔄 En cours : Extraction des métadonnées

## 🔄 En Cours de Développement

### Court Terme (v0.3.0)
- [x] Authentification de base
- [ ] Interface administrateur minimale
  - [ ] Tableau de bord
  - [ ] Gestion des utilisateurs
  - [ ] Vue des fichiers en traitement
- [ ] Connexion à AudioNexus
  - [ ] Configuration des instances
  - [ ] Synchronisation initiale

### Moyen Terme (v0.5.0)
- [ ] Gestion avancée des utilisateurs
- [ ] Tableau de bord complet
- [ ] Traitement par lots
- [ ] Analyse antivirus
- [ ] 2FA (Authentification à deux facteurs)

### Long Terme (v1.0.0)
- [ ] Gestion multi-instances
- [ ] Génération d'audiobooks depuis EPUB
- [ ] Synthèse vocale avancée
- [ ] Cluster AudioNexus

## 📂 Structure du Projet

```
audionexus/
├── backend/              # Application FastAPI
│   ├── app/
│   │   ├── api/          # Routeurs API
│   │   ├── core/         # Configuration de base
│   │   ├── db/           # Modèles de base de données
│   │   ├── models/       # Modèles Pydantic
│   │   ├── services/     # Logique métier
│   │   └── main.py       # Point d'entrée
│   ├── tests/            # Tests backend
│   └── requirements/     # Dépendances Python
│
├── frontend/            # Application React
│   ├── public/           # Fichiers statiques
│   └── src/
│       ├── components/   # Composants React
│       ├── pages/        # Pages de l'application
│       ├── store/        # Gestion d'état (Redux)
│       └── App.tsx      # Composant racine
│
├── docker/              # Configuration Docker
├── docs/                 # Documentation
└── scripts/              # Scripts utilitaires
```

## 🔧 Dépendances Principales

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy 2.0+
- PostgreSQL 14+
- Pydantic 2.0+
- JWT
- Bcrypt/Argon2

### Frontend
- React 18+
- TypeScript 5.0+
- Redux Toolkit
- React Query
- Material-UI/Chakra UI
- Axios

## 📚 Documentation

La documentation complète est organisée dans le dossier `documentation/` :

### Guides
- [Guide d'installation](guides/installation.md)
- [Guide d'utilisation](user-guide/usage.md)
- [Intégration avec Audiobookshelf](guides/audiobookshelf_integration.md)

### Référence
- [Documentation de l'API](api/)
- [Référence technique](reference/)

### Développement
- [Guide du développeur](development/)
- [Architecture](architecture/)
- [Décisions techniques](decisions/)

### Contribution
- [Code de conduite](contributing/CODE_OF_CONDUCT.md)
- [Guide de contribution](contributing/CONTRIBUTING.md)
- [Processus de développement](contributing/DEVELOPMENT.md)

### Génération Locale
```bash
# Installer les dépendances de documentation
pip install -r docs/requirements.txt

# Générer la documentation
cd docs && make html

# Ouvrir la documentation
xdg-open _build/html/index.html
```