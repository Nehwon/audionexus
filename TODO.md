# Plan de Développement - AudioNexus

## Notes
- **Projet** : AudioNexus, une plateforme de gestion centralisée pour les bibliothèques de livres audio, s'intégrant avec des instances Audiobookshelf.
- **Version actuelle** : 0.4.0-dev (refonte frontend en cours).
- **Stack Technique** :
  - **Backend** : Python/FastAPI, MySQL, SQLAlchemy 2.0, VoidAuth.
  - **Frontend** : Svelte, TypeScript, Tailwind CSS, VoidAuth.
  - **Infrastructure** : Docker, Docker Compose, Nginx.
  - **Outils** : FFmpeg pour le traitement audio.
- **Objectif principal** : Fournir une interface unifiée pour la gestion, le traitement et la synchronisation des fichiers audio sur plusieurs instances Audiobookshelf.
- **Avancement** : Correction des erreurs d'authentification et de validation Pydantic v2. Mise à jour de la documentation complète. **Problème en cours** : Résolution des erreurs de tests liées au paramètre 'kw' manquant dans les dépendances FastAPI.

## Stack Technique Détail

### Authentification - VoidAuth
- **Intégration** : Utilisation de VoidAuth pour la gestion complète de l'authentification
- **Fonctionnalités** :
  - Inscription/Connexion
  - Gestion des sessions
  - Récupération de mot de passe
  - Vérification d'email
  - MFA (Authentification à deux facteurs)
- **Documentation** : [GitHub VoidAuth](https://github.com/voidauth/voidauth)

### Frontend - Svelte + Tailwind CSS
- **Avantages** : 
  - Performances optimales
  - Taille réduite du bundle
  - Intégration native avec Tailwind
  - Meilleure expérience développeur


## Task List

### Immédiat (v0.4.0 - Refonte Frontend)
### Frontend (SvelteKit)
- [ ] **Configuration Initiale**
  - [ ] Initialiser un nouveau projet SvelteKit avec TypeScript
  - [ ] Configurer Tailwind CSS et Skeleton UI
  - [ ] Mettre en place la structure des dossiers
  - [ ] Configurer le routage de base

- [ ] **Authentification (VoidAuth)**
  - [ ] Intégrer VoidAuth dans le projet
  - [ ] Configurer les fournisseurs d'authentification
  - [ ] Personnaliser les templates d'email
  - [ ] Implémenter les callbacks personnalisés
  - [ ] Tester les flux d'authentification
- [ ] **Interface Utilisateur**
  - [ ] Tableau de bord principal
  - [ ] Gestion des fichiers/dossiers
  - [ ] Lecteur audio intégré
  - [ ] Thème sombre/clair
  - [ ] Interface responsive
### Backend (FastAPI)
- [ ] **Authentification**
  - [x] Système d'authentification JWT
  - [ ] Gestion des rôles et permissions
  - [ ] Mise à jour des tests unitaires

- [ ] **Gestion des Fichiers**
  - [ ] Téléversement de fichiers
  - [ ] Extraction d'archifs (ZIP, RAR)
  - [ ] Validation des fichiers audio
  - [ ] Stockage sécurisé
  - [ ] Conversion en M4B (FFmpeg)

- [ ] **Intégration Audiobookshelf**
  - [ ] Configuration des instances distantes
  - [ ] Synchronisation des bibliothèques
  - [ ] Gestion des métadonnées
  - [ ] Transfert sécurisé des fichiers
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

### Infrastructure
- [ ] **Docker**
  - [x] Configuration de base
  - [ ] Optimisation des conteneurs
  - [ ] Configuration de production

- [ ] **Sécurité**
  - [ ] Protection contre les attaques CSRF
  - [ ] Rate limiting
  - [ ] Journalisation des accès
  - [ ] Chiffrement des données sensibles

### Moyen Terme (v0.5.0)
- [ ] **Fonctionnalités Avancées**
  - [ ] Traitement par lots
  - [ ] Authentification à deux facteurs (2FA)
  - [ ] Gestion de plusieurs instances Audiobookshelf
  - [ ] Tableau de bord avancé (métriques, rapports)

### Long Terme (v1.0.0)
- [ ] **Fonctionnalités Premium**
  - [ ] Génération de livres audio depuis EPUB
  - [ ] Synthèse vocale intégrée
  - [ ] Cluster haute disponibilité
  - [ ] API publique pour développeurs

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