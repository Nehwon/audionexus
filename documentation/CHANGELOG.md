# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Non publié]

### Ajouté
- Logs de débogage avancés pour l'endpoint d'inscription utilisateur
- Gestion des erreurs détaillée pour le processus d'inscription

### Modifié
- Amélioration de la gestion des sessions asynchrones dans les endpoints d'API
- Refactorisation de la configuration de la base de données asynchrone
- Mise à jour de la documentation technique des endpoints d'authentification

### Corrigé
- Problème de dépendance circulaire dans l'initialisation de la base de données
- Erreur 500 lors de l'inscription utilisateur
- Gestion incorrecte des paramètres de session dans les dépendances FastAPI
- Problèmes de configuration de SQLite pour les tests

## [0.3.6] - 2025-07-21

### Modifié
- Mise à jour des endpoints d'authentification pour supporter Pydantic v2
- Amélioration de la gestion des erreurs dans les endpoints d'API
- Mise à jour de la documentation des endpoints

### Corrigé
- Résolution des erreurs 500 dans les endpoints d'authentification
- Correction de la gestion des sessions asynchrones
- Problèmes de validation des modèles Pydantic v2
- Configuration des tests pour utiliser SQLite in-memory

## [0.3.5] - 2025-06-27

### Modifié
- Migration de PostgreSQL vers MySQL pour la base de données de production
- Mise à jour de la configuration Docker pour supporter MySQL
- Correction des problèmes de configuration OAuth2
- Amélioration de la gestion des sessions de base de données

### Corrigé
- Correction des erreurs 500 dans les tests d'authentification
- Résolution des problèmes de dépendances circulaires
- Correction de la configuration des tests avec SQLite in-memory
- Mise à jour des dépendances pour la compatibilité avec Python 3.11

## [0.3.4] - 2025-06-26

### Modifié
- Passage de la licence de MIT à AGPL-3.0-or-later
- Mise à jour des informations d'auteur avec les coordonnées complètes
- Refonte du README pour une meilleure organisation
- Mise à jour des métadonnées dans pyproject.toml et package.json
- Création du fichier de licence AGPL-3.0-or-later
- Mise à jour de la version à 0.3.4

### Corrigé
- Correction des liens dans la documentation
- Uniformisation des informations de copyright

## [0.3.3] - 2025-06-20

### Corrigé
- Correction des chemins d'importation suite à la restructuration du projet
- Ajout de la dépendance manquante `email-validator` pour la validation des emails avec Pydantic
- Déplacement de l'initialisation de la base de données dans le cycle de vie de l'application
- Suppression des fichiers obsolètes et nettoyage du projet
- Mise à jour de la documentation de développement

### Modifié
- Amélioration de la structure des imports pour une meilleure maintenabilité
- Mise à jour du fichier `pyproject.toml` avec les dépendances requises
- Documentation des changements dans le fichier CHANGELOG.md

## [0.3.2] - 2025-06-18

### Ajouté
- Implémentation complète du système d'authentification frontend
- Configuration des routes protégées avec React Router
- Création des pages principales (Dashboard, Utilisateurs, Paramètres, 404)
- Mise en place du contexte d'authentification (AuthProvider)
- Configuration de l'API avec intercepteurs Axios
- Intégration de React Query pour la gestion des données
- Configuration de Chakra UI avec thème personnalisé
- Gestion des tokens JWT (stockage et rafraîchissement automatique)
- Configuration Docker pour le développement local
- Documentation mise à jour pour le démarrage du projet

### Modifié
- Simplification de la configuration Nginx pour le développement local
- Correction des erreurs de typage TypeScript
- Amélioration de la structure des dossiers frontend
- Mise à jour des dépendances frontend
- Optimisation des imports et résolution des avertissements de linting

## [0.3.1] - 2025-06-17

### Modifié
- Clarification de la distinction entre AudioNexus et Audiobookshelf
- Mise à jour des dépendances du projet
- Amélioration de la documentation utilisateur
- Correction des noms de conteneurs dans la configuration Docker

## [0.3.0] - 2025-06-16

### Changements majeurs
- Renommage du projet en "AudioNexus"
- Refonte complète de l'architecture technique
- Nouvelle structure de projet avec séparation frontend/backend
- Mise à jour de la documentation technique

### Ajouté
- Architecture frontend React/TypeScript avec Chakra UI
- Système d'authentification sécurisé
- Tableau de bord administrateur
- Gestion des fichiers multimédias
- Documentation technique complète
- Workflow de développement CI/CD
- Support de l'intégration avec Audiobookshelf

### Modifié
- Structure des dossiers pour une meilleure organisation
- Documentation du projet mise à jour
- Configuration Docker optimisée

## [0.2.0] - 2023-11-15

### Ajouté
- Fichier d'état du projet (ETAT_DU_PROJET.md)
- Documentation sur la structure du projet
- Planification des prochaines étapes

### Modifié
- Organisation de la documentation
- Mise à jour du README principal
- Nettoyage des doublons dans le CHANGELOG

### Ajouté
- Structure initiale du projet avec FastAPI et SQLAlchemy
- Configuration de base avec variables d'environnement
- Modèles de données pour les utilisateurs, bibliothèques et livres
- Client API pour interagir avec Audiobookshelf
- Configuration Docker avec PostgreSQL et Nginx
- Documentation complète dans README.md

### Modifié
- Organisation du code en modules logiques
- Amélioration de la gestion des erreurs
- Mise à jour de la documentation

### Ajouté
- Client API complet pour Audiobookshelf
- Gestion de l'authentification JWT
- Configuration Docker Compose
- Documentation d'API avec Swagger UI
- Tests unitaires de base

### Modifié
- Structure des réponses API
- Gestion des dépendances
- Configuration de la base de données

## [0.1.0] - 2023-10-01

### Ajouté
- Initialisation du projet
- Configuration de base de FastAPI
- Modèles de données initiaux
- Documentation de base
# Changelog

## [0.2.0] - 2025-06-15 23:30
### Ajouté
- Client Python complet pour l'API Audiobookshelf
- Documentation de l'API dans le README
- Exemple d'utilisation du client API
- Fichier .env.example pour la configuration
- Gestion des dépendances Python
- Support de l'authentification JWT
- Méthodes pour gérer les bibliothèques, livres, collections, etc.
- Configuration Docker Compose
- Fichier Dockerfile optimisé
- Configuration Nginx avec support SSL

## [0.1.0] - 2025-06-15 22:45
### Ajouté
- Structure de base du projet
- Documentation initiale (README.md)
- Script d'automatisation pour la conversion en M4B (automate.sh)
- Documentation pour m4b-tool

### Modifié
- Organisation du dépôt
- Documentation du projet

### Supprimé
- Anciens fichiers temporaires

## [0.0.1] - 2025-06-15
- Initialisation du dépôt
