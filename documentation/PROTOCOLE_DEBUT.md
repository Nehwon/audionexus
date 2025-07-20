# Protocole de Début de Session

Ce document décrit les étapes à suivre pour démarrer une session de travail sur le projet AudioNexus de manière organisée et efficace.

## 1. Vérifications Initiales

### 1.1. État du Dépôt
- [ ] Vérifier l'état actuel du dépôt Git
  ```bash
  git status
  ```
- [ ] S'assurer qu'aucune modification non commitée n'est en attente
- [ ] Si des modifications sont présentes, les mettre de côté ou les committer

### 1.2. Mise à Jour du Code
- [ ] Récupérer les derniers changements
  ```bash
  git fetch origin
  ```
- [ ] Vérifier les branches distantes mises à jour
  ```bash
  git branch -vva
  ```
- [ ] Mettre à jour la branche principale locale
  ```bash
  git checkout develop
  git pull --rebase
  ```

## 2. Configuration de l'Environnement

### 2.1. Variables d'Environnement
- [ ] Vérifier que le fichier `.env` est présent et correctement configuré
- [ ] S'assurer que les fichiers de configuration locaux sont à jour

### 2.2. Dépendances
- [ ] Mettre à jour les dépendances du backend
  ```bash
  docker-compose exec backend pip install -e ".[dev]"
  ```
- [ ] Mettre à jour les dépendances du frontend
  ```bash
  cd audionexus/frontend
  npm install
  ```

## 3. Documentation

- [ ] Consulter la documentation du projet
  ```bash
  # Ouvrir la documentation dans le navigateur
  open documentation/README.md
  # Ou consulter directement les fichiers Markdown dans les sous-dossiers thématiques
  ```
- [ ] Vérifier les mises à jour de la documentation
- [ ] Si nécessaire, générer une nouvelle documentation
  ```bash
  # Générer la documentation de l'API
  pdoc --html -o documentation/api app --force
  ```

## 4. Démarrage des Services

### 4.1. Services Docker
- [ ] Démarrer les services en arrière-plan
  ```bash
  docker-compose up -d
  ```
- [ ] Vérifier l'état des conteneurs
  ```bash
  docker-compose ps
  ```

### 3.2. Base de Données
- [ ] Vérifier que la base de données est accessible
  ```bash
  docker-compose exec db pg_isready
  ```
- [ ] Appliquer les migrations si nécessaire
  ```bash
  docker-compose exec backend alembic upgrade head
  ```

### 3.3. Services Frontend
- [ ] Démarrer le serveur de développement frontend
  ```bash
  cd audionexus/frontend
  npm run dev
  ```

## 4. Vérifications Finales

### 4.1. Accès aux Applications
- [ ] Vérifier l'accès à l'application frontend : http://localhost:3000
- [ ] Vérifier l'accès à l'API : http://localhost:8000
- [ ] Vérifier l'accès à la documentation de l'API : http://localhost:8000/docs

### 4.2. Tests Automatisés
- [ ] Exécuter les tests du backend
  ```bash
  docker-compose exec backend pytest
  ```
- [ ] Exécuter les tests du frontend
  ```bash
  cd audionexus/frontend
  npm test
  ```

## 5. Préparation au Développement

### 5.1. Création d'une Branche
- [ ] Créer une nouvelle branche pour la fonctionnalité
  ```bash
  git checkout -b type/description-courte
  ```
  - Types : `fix/`, `feature/`, `refactor/`, `docs/`, `chore/`

### 5.2. Initialisation de la Session
- [ ] Noter l'heure de début de session
  ```bash
  date
  ```
- [ ] Définir les objectifs de la session
  - Lister les tâches prioritaires
  - Estimer le temps nécessaire

## 6. Vérifications Finales

- [ ] Toutes les étapes précédentes ont été cochées ou explicitement rayées
- [ ] Tous les problèmes ont été documentés
- [ ] L'environnement est correctement configuré
- [ ] La branche de travail est prête pour le développement

## 7. Phase de Développement

Une fois l'initialisation terminée :
1. Consulter la liste des tâches identifiées
2. Traiter chaque tâche une par une
3. Tester chaque modification
4. Documenter les changements

---
*Document de procédure - Ne pas modifier ce fichier pour y ajouter des notes de session spécifiques*
