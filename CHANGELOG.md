# 📜 CHANGELOG.md - Historique des Versions AudioNexus

Ce document recense toutes les versions d'AudioNexus avec leurs changements significatifs.

---

## 📦 Versions Actuelles

### v0.14.0 (20/04/2026)
**Commit**: 2563632
- **Réorganisation majeure du projet** : Structure complète refactorée
- **Nouveaux dossiers** : config/, docker/, archives/, scripts/, Pull_Request/
- **40+ fichiers déplacés** : Meilleure organisation et séparation des préoccupations
- **Templates ajoutés** : PULL_REQUEST_TEMPLATE.md et PR_REORGANISATION_DESCRIPTION.md
- **Documentation mise à jour** : Tous les fichiers .md mis à jour

### v0.12.19 (19/04/2026)
**Commit**: 8d0ab3c
- Ajout de la documentation MEMORY.md et WORKFLOWS.md
- Mise à jour du README avec l'état post-debug
- Synchronisation des branches debug et devel

### v0.12.18 (19/04/2026)
**Commit**: bc08337
- Merge de devel vers debug avec résolution des conflits
- Correction des warnings MySQL dans tous les docker-compose
- Ajout de la tâche de migration PostgreSQL dans TODO.md

### v0.12.17 (19/04/2026)
**Commit**: cf2d182
- Correction des warnings MySQL (remplacement --skip-host-cache)
- Ajout de la tâche de migration PostgreSQL
- Mise à jour des fichiers docker-compose.yml

### v0.12.16 (19/04/2026)
**Commit**: b004aa4
- Suppression des tests du workflow CI/CD comme demandé
- Optimisation du pipeline de build

### v0.12.8 (19/04/2026)
**Commit**: 8fb4b47
- Version finale après analyse des commits
- Système de versionnement automatique implémenté
- Corrections des noms de repository en minuscules

---

## 📚 Historique des Versions Principales

### v0.8.0 (07/09/2025)
**Commit**: dd51bc3
- **PHASE 5 TERMINÉE** - AudioNexus PRODUCTION-READY
- Implémentation complète de l'interface audiobooks
- Synchronisation multi-instances Audiobookshelf
- Dashboard admin avec métriques temps réel
- Interface de téléversement avec traitement automatique
- Documentation complète mise à jour

### v0.5.0 (04/09/2025)
**Commit**: 447486d
- Implémentation interface audiobooks Phase A & C
- Corrections complètes ROADMAP.md et TODO.md
- Succès mission authentication
- Résolution des échecs de connexion

### v0.3.3 (03/09/2025)
**Commit**: 19:731fb72
- Migration vers MySQL et corrections OAuth2
- Architecture unifiée MySQL/SQLite
- Optimisations Docker complètes

### v0.1.0 (02/09/2025)
**Commit**: 2170545
- Version initiale de reset
- Structure de base du projet
- Configuration initiale

---

## 🔄 Versions de Développement Intermédiaires

### v0.16.0 (19/04/2026)
**Commit**: 6d3d7ec
- Version basée sur l'analyse des commits
- Préparation pour les corrections majeures

### v0.12.0 - v0.12.19 (19/04/2026)
Série de versions de debug et corrections:
- Gestion des threads FFmpeg
- Corrections CI/CD
- Optimisations Docker
- Documentation améliorée

---

## 📋 Versions Historique (Avant Reset)

### v0.8.0 - v0.11.0 (07/09/2025 - 19/04/2026)
Période de développement intense avec:
- Implémentation complète des fonctionnalités core
- Optimisations de performance
- Tests E2E complets
- Processing métadonnées avancé
- Sécurité renforcée

### v0.1.0 - v0.7.0 (02/09/2025 - 06/09/2025)
Développement initial:
- Structure de base
- Authentification initiale
- Première interface utilisateur
- Configuration Docker

---

## 🔧 Versions Techniques et Corrections

### Corrections FFmpeg (19/04/2026)
**Commits**: ec6e8c5, 89022cb, b11e789, 265fbb19
- Fix FFmpeg thread management
- Ajout de tests complets pour la gestion des threads
- Correction des services d'upload
- Mise à jour de la documentation

### Corrections CI/CD (19/04/2026)
**Commits**: 5f219d0, 0a809e9, e77b367, 91f94be
- Remplacement du CI/CD basé sur AWS par GitHub Container Registry
- Implémentation du système multi-branches
- Correction des problèmes de cache Docker
- Optimisation des workflows

### Corrections Docker (19/04/2026)
**Commits**: d83fea0, 84f221c, bb4fc8f, 729702d
- Correction des noms de repository en minuscules
- Fix des tags GHCR
- Amélioration des builds multi-architectures
- Optimisation des caches

---

## 📊 Statistiques des Versions

- **Total des versions**: 20+ versions majeures et mineures
- **Période couverte**: 02/09/2025 - 19/04/2026
- **Commits analysés**: 50+ commits significatifs
- **Documentation**: Complète et à jour

---

## 📝 Conventions de Versionnement

AudioNexus utilise le versionnement sémantique:

- **MAJOR** (vX.0.0): Changements incompatibles
- **MINOR** (v0.X.0): Nouvelles fonctionnalités compatibles
- **PATCH** (v0.0.X): Corrections de bugs compatibles

Les versions de debug suivent le format v0.M.f où M représente la série de debug.

---

*Dernière mise à jour: 19/04/2026*
*Version actuelle: v0.12.19*