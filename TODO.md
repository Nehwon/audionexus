# Plan de Développement - AudioNexus

## Notes
- **Projet** : AudioNexus, une plateforme de gestion centralisée pour les bibliothèques de livres audio, s'intégrant avec des instances Audiobookshelf.
- **Version actuelle** : 0.3.6-dev (en développement actif).
- **Stack Technique** :
  - **Backend** : Python/FastAPI, SQLite (développement), PostgreSQL (production), SQLAlchemy 2.0.
  - **Frontend** : React/TypeScript, Chakra UI, Redux Toolkit, React Query.
  - **Infrastructure** : Docker, Docker Compose.
- **Objectif principal** : Fournir une interface unifiée pour la gestion, le traitement et la synchronisation des fichiers audio sur plusieurs instances Audiobookshelf.
- **Avancement** : Correction des erreurs d'authentification et de validation Pydantic v2. Mise à jour de la documentation complète. **Problème en cours** : Résolution des erreurs de tests liées au paramètre 'kw' manquant dans les dépendances FastAPI.

## Task List

### Court Terme (v0.3.x)
- [x] **Mise en Place du Backend**
  - [x] Créer la structure du projet FastAPI.
  - [x] Implémenter le modèle de données utilisateur (SQLAlchemy).
  - [x] Implémenter les schémas de validation (Pydantic).
  - [x] Développer le service d'authentification (logique métier).
  - [x] Créer les routes API pour l'authentification (`/login`, `/register`, `/refresh`, `/me`).
- [x] **Finaliser l'Authentification (Frontend)**
  - [x] Connecter la page de connexion (`LoginPage.tsx`) à l'API backend.
  - [x] Gérer le stockage des tokens JWT (access & refresh) côté client.
  - [x] Mettre en place des routes protégées.
  - [x] Implémenter la logique de déconnexion.
  - [x] Implémenter la réinitialisation de mot de passe (UI + API call).
- [x] **Nettoyage et Fiabilisation du Frontend**
  - [x] Corriger les erreurs de linting restantes (imports, types, etc.).
  - [x] Mettre à jour `App.tsx` pour intégrer le routage et le `AuthProvider`.
  - [x] Mettre en place le routage principal de l'application avec les routes protégées.
- [x] **Configuration de l'Environnement et Lancement**
  - [x] Modifier les fichiers `.gitignore` pour autoriser la création du fichier `.env`.
  - [x] Créer le fichier `.env` avec les variables de développement.
  - [x] Lancer les services backend avec `docker compose`.
  - [x] Simplifier la configuration Nginx pour le développement local (HTTP uniquement).
  - [x] Redémarrer les services Docker pour appliquer la nouvelle configuration Nginx.
  - [x] **Résoudre le problème de démarrage du backend**
    - [x] Identifier la cause de l'erreur `ModuleNotFoundError: No module named 'app'`.
    - [x] Corriger les chemins d'importation dans le code source.
    - [x] Ajouter les dépendances manquantes (email-validator).
    - [x] Mettre à jour le `Dockerfile` pour une construction et une exécution robustes.
    - [x] Vérifier le bon démarrage du service backend.
  - [x] Lancer le serveur de développement frontend.
  - [x] Vérifier que l'application est accessible et fonctionnelle.
  - [ ] Lancer le serveur de développement frontend.
  - [ ] Vérifier que l'application est accessible et fonctionnelle.
- [x] **Finalisation de la session et mise à jour de la documentation**
  - [x] Mettre à jour le fichier `developpement.md`.
  - [x] Mettre à jour le fichier `ETAT_DU_PROJET.md`.
  - [x] Mettre à jour le fichier `README.md` principal et les autres README du projet.
  - [x] Commiter toutes les modifications en attente.
  - [x] Pousser les commits vers le dépôt distant.
- [ ] **Interface Administrateur Minimale** (Priorité Haute)
  - [x] Développer le tableau de bord principal (vue d'ensemble, état des instances).
  - [x] Créer la page de gestion des utilisateurs.
  - [x] Créer la page des paramètres.
  - [ ] Mettre en place la vue des fichiers en cours de traitement.
- [ ] **Correction des Tests d'Authentification** (Priorité Critique)
  - [ ] Résoudre l'erreur liée au paramètre 'kw' manquant dans les dépendances FastAPI.
  - [ ] Mettre à jour les tests pour refléter les changements de la validation Pydantic v2.
  - [ ] Vérifier la couverture des tests pour les endpoints critiques.

- [ ] **Intégration Audiobookshelf** (Priorité Moyenne)
  - [ ] Permettre la configuration des instances Audiobookshelf.
  - [ ] Gérer l'authentification et les tokens pour l'API Audiobookshelf.
  - [ ] Implémenter la synchronisation initiale (bibliothèques, métadonnées, utilisateurs).
- [ ] **Gestion des Fichiers de Base** (Priorité Moyenne)
  - [ ] Mettre en place une zone de dépôt sécurisée.
  - [ ] Gérer le téléversement et l'extraction de fichiers compressés.

### Moyen Terme (v0.5.0)
- [ ] Gestion avancée des utilisateurs (rôles, permissions).
- [ ] Tableau de bord complet (métriques, rapports, alertes).
- [ ] Traitement des fichiers par lots.
- [ ] Implémenter l'authentification à deux facteurs (2FA).
- [ ] Gestion de plusieurs instances Audiobookshelf.

### Long Terme (v1.0.0)
- [ ] Génération de livres audio à partir de fichiers EPUB.
- [ ] Intégration de la synthèse vocale.
- [ ] Mise en place d'un cluster AudioNexus pour la haute disponibilité.

## Prochaines Étapes (Priorité)
1. Résoudre l'erreur liée au paramètre 'kw' manquant dans les dépendances FastAPI.
2. Mettre à jour les tests pour refléter les changements de la validation Pydantic v2.
3. Finaliser la migration vers SQLAlchemy 2.0 et la gestion unifiée des sessions asynchrones.
4. Nettoyer les dépendances circulaires restantes.
5. Améliorer la couverture des tests pour atteindre au moins 80%.
6. Préparer la migration vers la base de données de production (MySQL/PostgreSQL).
7. Mettre à jour la documentation technique avec les nouvelles fonctionnalités et corrections.

## Dernières Modifications
- 2025-07-21 : Correction des erreurs de validation Pydantic v2 et mise à jour de la documentation.
- 2025-07-20 : Résolution des erreurs 500 dans l'endpoint /auth/register.
- 2025-07-19 : Mise à jour de la version à 0.3.6-dev et nettoyage du code.
- 2025-06-20 : Correction des tests d'authentification et configuration de la base de données de test.
- 2025-06-20 : Mise à jour de la documentation et du plan de développement.