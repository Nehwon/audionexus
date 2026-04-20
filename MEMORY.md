# 🧠 MEMORY.md - Mémoire du Projet AudioNexus

Ce document centralise les informations critiques à conserver en mémoire pour le développement et la maintenance d'AudioNexus.

---

## 📋 Historique des Réorganisations Majeures

### Réorganisation v0.14.0 (20/04/2026)
**Objectif**: Nettoyer la racine du projet et améliorer la maintenabilité

**Changements:**
- Création de 5 nouveaux dossiers: `config/`, `docker/`, `archives/`, `scripts/`, `Pull_Request/`
- Déplacement de 40+ fichiers techniques depuis la racine
- Conservation des fichiers de documentation core à la racine
- Ajout de templates pour les Pull Requests

**Structure avant:**
```
.
├── 40+ fichiers techniques
├── fichiers de documentation
└── code source
```

**Structure après:**
```
.
├── app/                  # Code source
├── config/               # Configuration
├── docker/               # Docker
├── archives/             # Temporaires
├── scripts/              # Scripts
├── Pull_Request/         # Templates
├── documentation core    # À la racine
└── AudioNexus.code-workspace
```

**Bénéfices:**
- Meilleure séparation des préoccupations
- Navigation plus intuitive
- Conformité aux meilleures pratiques
- Facilite l'onboarding des nouveaux développeurs

---

## 🔑 Concepts Clés à Retenir

### 1. Architecture Globale
- **Frontend**: React/TypeScript avec Vite
- **Backend**: FastAPI avec SQLAlchemy
- **Base de données**: MySQL (avec migration prévue vers PostgreSQL)
- **Cache**: Redis
- **Conteneurisation**: Docker avec multi-stage builds
- **CI/CD**: GitHub Actions

### 2. Système de Versionnement
- Format: `vM.m.f` (ex: v0.12.18)
- Géré automatiquement via `scripts/auto_bump_version.py`
- Déclenché par les commits et merges
- Fichier VERSION à la racine

### 3. Workflow Git
- **Branches principales**:
  - `main`: Production stable
  - `devel`: Développement principal
  - `debug`: Branche de debug et corrections
  - `preprod`: Pré-production et tests finaux
- **Feature branches**: `feature/*` pour les nouvelles fonctionnalités
- **Protocole de merge**: 
  - Les corrections de debug sont mergées vers devel
  - Les features sont mergées vers devel après review
  - La préproduction est mergée vers main pour les releases

### 4. Configuration Docker
- Services principaux: frontend, backend, db (MySQL), redis, adminer
- Volumes persistants pour la base de données
- Health checks configurés pour tous les services
- Commandes MySQL optimisées (remplacement de `--skip-host-cache` par `--host-cache-size=0`)

### 5. Points d'Attention Critiques

#### Backend
- **UploadService**: Gestion des threads FFmpeg avec `start_new_session=True`
- **Timeouts**: 30min pour conversions simples, 1h pour concaténations
- **Terminaison propre**: Annulation explicite des processus FFmpeg
- **Conflits SQLAlchemy**: Doublon de table `audit_logs` à corriger

#### Frontend
- **AudiobookUploader**: Drag&drop déjà implémenté avec react-dropzone
- **SearchComponent**: Pagination et suggestions à finaliser
- **Navigation**: Routes vers les pages de détail à implémenter

#### Infrastructure
- **MySQL warnings**: Corrigés avec `--host-cache-size=0`
- **Migration PostgreSQL**: À planifier pour meilleure scalabilité
- **Redis**: Connexion à configurer pour les tests locaux

---

## 📋 Décisions Architecturales Importantes

### 1. Gestion des Uploads
- **Approche**: Traitement asynchrone avec polling
- **Sécurité**: Validation stricte des fichiers (taille, extensions, MIME types)
- **Metadata**: Extraction automatique via Mutagen
- **Conversion**: FFmpeg pour normalisation au format M4B

### 2. Authentification
- **Système**: VoidAuth (OIDC)
- **Implémentation**: Complète mais à documenter
- **Sécurité**: JWT avec rotation des clés

### 3. Base de Données
- **Actuel**: MySQL 8.0 avec InnoDB
- **Futur**: Migration vers PostgreSQL prévue
- **ORMA**: SQLAlchemy avec Alembic pour les migrations

### 4. Tests
- **Stratégie**: Tests unitaires uniquement (pas d'intégration dans CI/CD)
- **Couverture**: Focus sur les services critiques (upload, auth)
- **Outils**: pytest avec fixtures Docker

---

## 🔄 Workflows et Processus

### 1. Développement Standard
```
feature/xxx → devel → preprod → main
```

### 2. Debug et Corrections
```
devel → debug (corrections) → devel (merge)
```

### 3. Release Process
1. Merge devel → preprod
2. Tests complets en préproduction
3. Mise à jour de la documentation
4. Merge preprod → main avec tag de version
5. Build et push des images Docker

### 4. Gestion des Versions
- **Bump automatique**: À chaque commit/merge significatif
- **Types de bump**:
  - `fix`: Corrections de bugs
  - `feat`: Nouvelles fonctionnalités
  - `BREAKING CHANGE`: Changements majeurs

---

## ⚠️ Problèmes Connus et Solutions

### 1. MySQL Warnings
**Problème**: Messages de dépréciation pour `--skip-host-cache`
**Solution**: Remplacé par `--host-cache-size=0` dans tous les docker-compose

### 2. Conflit SQLAlchemy
**Problème**: Doublon de définition pour `audit_logs`
**Solution**: À corriger dans `app/db/models/audit.py`

### 3. Redis Local
**Problème**: Connexion refusée sans serveur Redis
**Solution**: Lancer Redis localement ou utiliser Docker

### 4. Tests d'Intégration
**Problème**: Échec de collecte des tests
**Solution**: Vérifier la configuration pytest et les dépendances

---

## 📚 Documentation de Référence

- **TODO.md**: Liste complète des tâches en cours
- **ROADMAP.md**: Feuille de route stratégique
- **documentation/**: Documentation technique détaillée
- **scripts/**: Scripts utilitaires et d'automatisation

---

*Dernière mise à jour: 20/04/2026*