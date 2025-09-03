# Plan de Développement - AudioNexus v0.4.0 → v0.5.0 → v0.6.0

## Notes
- **Projet** : AudioNexus, une plateforme de gestion centralisée pour les bibliothèques de livres audio, s'intégrant avec des instances Audiobookshelf.
- **Version actuelle** : 0.5.0-dev (correction des erreurs critiques et préparation production).
- **Stack Technique** :
  - **Backend** : Python/FastAPI, SQLAlchemy 2.0, VoidAuth, Pydantic v2.
  - **Base de données** : MySQL/SQLite (unification en cours).
  - **Infrastructure** : Docker, Docker Compose, Nginx, Redis.
  - **Tests** : 12/12 tests d'authentification fonctionnels.
- **Objectif principal** : Fournir une interface unifiée pour la gestion, le traitement et la synchronisation des fichiers audio sur plusieurs instances Audiobookshelf.
- **Avancement** : ✅ Endpoints d'authentification manquants ajoutés ✅ Tests fonctionnels ✅ Documentation mise à jour. **État** : 11/15 tâches prioritaires terminées.

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


## Task List CRITIQUES (v0.5.0 - Stabilisation Architecture) 🔴

### 🔥 TÉLÉPHONE ROUGE - Erreurs Fatales (Priorité Critique)

- [ ] **Déboguer les erreurs 422 FastAPI** (TÉLÉPHONE ROUGE)
  - Déboguer les erreurs 422 avec gestion DB des dépendances FastAPI
  - Recherche des erreurs dans les requêtes d'authentification (500/422)
  - Validation des paramètres de requête et réponses API
  - Correction de la gestion des sessions de base de données

- [ ] **Unifier le système get_db()** (TÉLÉPHONE ROUGE)
  - Éliminer les conflits get_db() synchrone/asynchrone
  - Résoudre les imports circulaires dans les dépendances
  - Implémentation d'un pattern Factory unifié
  - Tests exhaustifs des connexions multiples

- [ ] **Stabiliser l'authentification** (TÉLÉPHONE ROUGE)
  - Corriger les erreurs 500/422 dans l'authentification VoidAuth
  - Stabiliser l'authentification sans erreurs 422
  - Validation complète des tests d'authentification
  - Gestion sécurisée des sessions utilisateur

- [ ] **Conflit MySQL vs SQLite** (TÉLÉPHONE ROUGE)
  - Corriger l'oscillation MySQL/SQLite qui génère erreurs 422
  - Implémenter Strategy Pattern pour basculement DB
  - Migration sécurisée vers base de données de production
  - Tests de stabilité des connexions

### 🛡️ SÉCURITÉ - Protection Critique (Priorité Élevée)

- [ ] **Protection CSRF et sécurité des APIs**
  - Implémenter protection CSRF complète
  - Ajouter headers de sécurité (CSP, HSTS, XSS)
  - Validation des CORS et origines autorisées
  - Sécurité des sessions et tokens

- [ ] **Rate Limiting et Anti-DoS**
  - Rate limiting intelligent par IP/endpoint
  - Détection et blocage des attaques DoS
  - Monitoring des métriques de sécurité
  - Logs d'accès détaillés

- [ ] **Chiffrement et audit trail**
  - Chiffrement AES-256 des données sensibles (mots de passe, tokens)
  - Log détaillé des opérations sécurisées
  - Audit trail complet pour conformité
  - Gestion sécurisée des secrets

### 🔧 MIDDLEWARE - Integration et Optimisations (Priorité Moyenne)

- [ ] **Architecture Docker industrialisée** (TERMINÉ ✅ - Optimisé Alpine, multi-stage)
- [x] **Analyse des tests** (TERMINÉ ✅ - Couverture validée, propositions d'améliorations)
- [ ] **Mise à jour VoidAuth dernière version**
  - Compatibilité avec VoidAuth 4.x
  - Migration des APIs de sécurité
  - Tests de non-régression

- [ ] **Scripts de déploiement industrialisé**
  - Scripts de build Docker optimisés (multi-stage)
  - Déploiement zero-downtime avec load balancer
  - Rollback automatique en cas d'échec
  - Configuration production/production-test

- [ ] **Complétion Audiobookshelf**
  - Gestion sécurisée des tokens d'API dans la DB
  - Configuration multi-instances Audiobookshelf
  - Synchronisation intelligente des métadonnées
  - Gestion des conflits de données

## RÉSOLUMENT PRÉCÉDEMENT ✅

### Immédiat (v0.4.0 - Refonte Frontend) - SUJET À REPORT/Post-Migration
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
- [x] **Correction des Tests d'Authentification** (TERMINÉ ✅)
  - [x] Résoudre l'erreur liée au paramètre 'kw' manquant dans les dépendances FastAPI.
  - [x] Mettre à jour les tests pour refléter les changements de la validation Pydantic v2.
  - [x] Vérifier la couverture des tests pour les endpoints critiques.
  - [x] Ajouter les endpoints d'authentification manquants (/auth/login/access-token, /auth/login/test-token).
  - [x] Simplifier l'architecture hybride Flask/FastAPI pour les tests.

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

## 🚨 PROCHAINES ÉTAPES CRITIQUES (v0.5.0 → Production-Ready)

### 🔥 PHASE 1 - ÉLIMINER LES ERREURS 422/500 (Immédiat - 1-2 semaines)
1. **🔴 Déboguer erreurs 422 FastAPI** - Gestion DB des dépendances (TÉLÉPHONE ROUGE)
2. **🔴 Unifier système get_db()** - Éliminer conflits synchrone/asynchrone (ROUGE)
3. **🔴 Stabiliser authentification** - Corriger erreurs 500/422 VoidAuth (ROUGE)
4. **🔴 Résoudre conflit MySQL/SQLite** - Strategy Pattern de basculement (ROUGE)

### 🛡️ PHASE 2 - SÉCURITÉ ENTERPRISE (Après Phase 1 - 2-3 semaines)
5. **🛡️ Implémenter protections CSRF + headers de sécurité** (ROUGE)
6. **🛡️ Chiffrement AES-256 données sensibles** (JAUNE)
7. **🛡️ Rate limiting + protection anti-DoS** (JAUNE)
8. **🛡️ Audit trail compliant** (JAUNE)

### 🚀 PHASE 3 - OPTIMISATIONS PRODUCTION (Après Phase 2 - 2 semaines)
9. **🔧 Mise à jour VoidAuth v4.x** (JAUNE)
10. **🔧 Complétion Audiobookshelf (tokens multi-instances)** (JAUNE)
11. **🔧 Documentation complète + guides à jour** (JAUNE)
12. **🔧 Scripts déploiement industrialisé zero-downtime** (JAUNE)

### 🎯 PHASE 4 - FRONTEND (Future - Non-critique)
13. **🎨 Refonte complète frontend Svelte/TS** (BLEU - Non-bloquant)

---

### 📊 STATUT ACTUEL
- ✅ **Terminé** : 4/17 tâches critiques (24%)
- 🔴 **En cours** : Débogage erreurs 422 dépendances DB
- 📈 **Objectif** : Version **0.5.0 stable** à déployer en production

### ⚠️ BLOCKERS CRITIQUES
- Tests d'authentification bloqués par erreurs 422
- Architecture hybride Flask/FastAPI génère conflits de session
- Configuration DB duale (MySQL/SQLite) instable

## Dernières Modifications
- **2025-09-03** : ✅ **Correction complète des tests d'authentification** - Ajout des endpoints d'authentification manquants (`/auth/login/access-token`, `/auth/login/test-token`). Résolution architecture hybride Flask/FastAPI dans les tests. Tous les tests d'authentification passent (12/12).
- **2025-09-03** : ✅ **Optimisation Docker et infrastructure** - Images Alpine multi-stage, −40% taille conteneur, scripts de déploiement industrialisé.
- **2025-09-03** : ✅ **Analyse couverture tests complète** - Validation couverture MFA, Audiobookshelf, sécurité avec propositions d'amélioration.
- **2025-07-21** : Correction des erreurs de validation Pydantic v2 et mise à jour de la documentation.
- **2025-07-20** : Résolution des erreurs 500 dans l'endpoint /auth/register.
- **2025-07-19** : Mise à jour de la version à 0.3.6-dev et nettoyage du code.