# Protocole de Fin de Session

Ce document décrit les étapes pour terminer une session de travail sur le projet AudioNexus de manière organisée et professionnelle.

## 1. Mise à jour de la Documentation

### 1.1. Suivi des Versions
- [ ] Mettre à jour le fichier `CHANGELOG.md`
  - Ajouter une section pour les modifications en cours
  - Catégoriser les changements :
    - `Added` pour les nouvelles fonctionnalités
    - `Changed` pour les modifications de fonctionnalités existantes
    - `Deprecated` pour les fonctionnalités marquées comme obsolètes
    - `Removed` pour les fonctionnalités supprimées
    - `Fixed` pour les corrections de bugs
    - `Security` pour les vulnérabilités corrigées

### 1.2. État du Projet
- [ ] Mettre à jour `ETAT_DU_PROJET.md`
  - Actualiser la version actuelle
  - Mettre à jour l'état d'avancement
  - Documenter les problèmes connus
  - Mettre à jour la roadmap si nécessaire

### 1.3. Documentation Technique
- [ ] Mettre à jour la documentation du code
  - Ajouter/modifier les docstrings
  - Mettre à jour les commentaires
  - Documenter les décisions techniques importantes

## 2. Gestion de Version

### 2.1. Numérotation des Versions
- [ ] Déterminer le type de mise à jour nécessaire
  - `MAJOR` : Changements non rétrocompatibles
  - `MINOR` : Nouvelles fonctionnalités rétrocompatibles
  - `PATCH` : Corrections de bugs rétrocompatibles
- [ ] Mettre à jour le numéro de version dans les fichiers appropriés
  - `pyproject.toml` / `package.json` / etc.
  - Fichier de version dédié si existant

## 3. Vérifications de Qualité

### 3.1. Exécution des Tests
- [ ] Lancer la suite de tests complète
  ```bash
  # Backend
  docker-compose exec backend pytest
  
  # Frontend
  cd audionexus/frontend
  npm test
  ```
- [ ] Vérifier que tous les tests passent
- [ ] Documenter tout échec de test non résolu

### 3.2. Qualité du Code
- [ ] Exécuter les vérifications de style
  ```bash
  # Backend (Python)
  docker-compose exec backend flake8 .
  docker-compose exec backend black --check .
  
  # Frontend (TypeScript/React)
  cd audionexus/frontend
  npx eslint .
  npx prettier --check .
  ```
- [ ] Corriger les problèmes identifiés ou les documenter

## 4. Gestion du Code Source

### 4.1. Préparation du Commit
- [ ] Vérifier les modifications en attente
  ```bash
  git status
  ```
- [ ] Vérifier les différences
  ```bash
  git diff --staged
  ```
- [ ] Créer un commit avec un message clair
  ```bash
  git commit -m "type(scope): description concise des changements"
  ```
  - Types de commit recommandés :
    - `feat` : Nouvelle fonctionnalité
    - `fix` : Correction de bug
    - `docs` : Modification de la documentation
    - `style` : Formatage, point-virgule manquant, etc. (pas de changement de code)
    - `refactor` : Refactorisation du code de production
    - `test` : Ajout ou modification de tests
    - `chore` : Mise à jour des tâches de construction, gestionnaire de paquets, etc.

### 4.2. Synchronisation avec le Dépôt Distant
- [ ] Récupérer les derniers changements
  ```bash
  git pull --rebase
  ```
- [ ] Résoudre les éventuels conflits
- [ ] Pousser les modifications
  ```bash
  git push origin nom-de-la-branche
  ```

## 5. Documentation de la Session

### 5.1. Mise à jour du Suivi des Tâches
- [ ] Mettre à jour `TODO.md`
  - Cocher les tâches terminées
  - Ajouter les nouvelles tâches identifiées
  - Mettre à jour les priorités

### 5.2. Notes pour la Prochaine Session
- [ ] Documenter les points à reprendre
- [ ] Noter les problèmes non résolus
- [ ] Lister les prochaines étapes
- [ ] Estimer le temps nécessaire pour les tâches restantes

## 6. Nettoyage

### 6.1. Arrêt des Services
- [ ] Arrêter les conteneurs Docker
  ```bash
  docker-compose down
  ```
- [ ] Vérifier qu'aucun conteneur n'est en cours d'exécution
  ```bash
  docker ps -a
  ```
- [ ] Nettoyer les ressources inutilisées (optionnel)
  ```bash
  docker system prune -f
  ```

### 6.2. Nettoyage du Code
- [ ] Supprimer le code commenté inutile
- [ ] Supprimer les fichiers temporaires
- [ ] Nettoyer le cache des dépendances si nécessaire

### 6.3. Nettoyage des Données de Test
- [ ] Supprimer les conteneurs de test
  ```bash
  docker-compose -f docker-compose.test.yml down -v
  ```
- [ ] Nettoyer les volumes inutilisés
  ```bash
  docker volume prune -f
  ```
- [ ] Supprimer les images inutilisées
  ```bash
  docker image prune -f
  ```
- [ ] Vérifier l'état du système Docker
  ```bash
  docker system df
  ```

## 7. Vérifications Finales

- [ ] Tous les tests passent avec succès
- [ ] La documentation est à jour et cohérente
- [ ] Le code est conforme aux standards du projet
- [ ] Les modifications ont été testées localement
- [ ] Les changements ont été poussés sur le dépôt distant
- [ ] Les branches distantes sont à jour
- [ ] Les dépendances sont à jour et sécurisées

## 8. Clôture de la Session

- [ ] Noter l'heure de fin de session
  ```bash
  date
  ```
- [ ] Calculer le temps passé sur la session
- [ ] Mettre à jour le suivi du temps si nécessaire
- [ ] Fermer les applications et fichiers inutiles

---
*Document de procédure - Ne pas modifier ce fichier pour y ajouter des notes de session spécifiques*
