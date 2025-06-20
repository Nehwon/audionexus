# Protocole de Développement AudioNexus

## 📜 Règles Générales

1. **Langue** : Tous les commentaires, messages de commit et documentation doivent être en français.
2. **Style de code** : 
   - Python : Suivre les conventions PEP 8
   - Frontend : Standards React/TypeScript
   - Documentation : Format Markdown avec en-têtes clairs
3. **Branches** : Utiliser le modèle Git Flow avec les branches suivantes :
   - `main` : Branche de production (protégée, uniquement via MR)
   - `develop` : Branche d'intégration (branche principale de développement)
   - `feature/*` : Nouvelles fonctionnalités (ex: `feature/user-authentication`)
   - `fix/*` : Corrections de bugs (ex: `fix/login-error`)
   - `hotfix/*` : Corrections critiques pour la production (ex: `hotfix/security-issue`)
   - `chore/*` : Tâches de maintenance (ex: `chore/update-dependencies`)

## 🔄 Workflow de Développement

1. **Avant de commencer** :
   - Mettre à jour la branche `develop` : `git checkout develop && git pull`
   - Créer une nouvelle branche : `git checkout -b type/brief-description`
   - Mettre à jour le fichier `TODO.md` avec la tâche en cours

2. **Pendant le développement** :
   - Faire des commits atomiques avec des messages clairs
   - Format des messages : `type(portée): description`
     - Exemples :
       - `feat(auth): ajout de la connexion avec JWT`
       - `fix(api): correction de la validation des emails`
       - `docs(readme): mise à jour des instructions d'installation`
   - Types de commit : 
     - `feat` : Nouvelle fonctionnalité
     - `fix` : Correction de bug
     - `docs` : Documentation uniquement
     - `style` : Formatage, point-virgule manquant, etc.
     - `refactor` : Modification du code qui ne corrige pas un bug ni n'ajoute une fonctionnalité
     - `test` : Ajout ou modification de tests
     - `chore` : Mise à jour des tâches de build, gestionnaire de paquets, etc.
   - Mettre à jour régulièrement :
     - `CHANGELOG.md`
     - `README.md`
     - `TODO.md`

3. **Avant de pousser** :
   - Mettre à jour la branche `develop` : `git pull origin develop`
   - Résoudre les éventuels conflits
   - Exécuter les tests : `pytest` et `npm test`
   - Vérifier le linter : `pylint`, `mypy`, `eslint`
   - Mettre à jour `ETAT_DU_PROJET.md` si nécessaire

4. **Revue de code** :
   - Pousser la branche : `git push -u origin nom-de-la-branche`
   - Créer une Merge Request (MR) vers `develop`
   - Assigner au moins un relecteur
   - Mettre à jour la description de la MR avec les changements effectués
   - Résoudre les commentaires de la revue
   - Mettre à jour `ETAT_DU_PROJET.md` avec l'avancement

5. **Après validation** :
   - Fusionner la branche avec `develop` (via merge commit)
   - Supprimer la branche distante après fusion
   - Mettre à jour `CHANGELOG.md` avec les changements de la version
   - Taguer la version si nécessaire : `git tag -a v1.0.0 -m "Version 1.0.0"`

## 🐳 Développement avec Docker

### Services disponibles
- `backend` : API FastAPI (port 8000)
- `db` : PostgreSQL 15 (port 5432)
- `redis` : Cache et files d'attente (port 6379)
- `nginx` : Reverse proxy (ports 80/443)
- `certbot` : Gestion des certificats SSL

### Commandes essentielles
```bash
# Démarrer tous les services
docker compose up -d

# Suivre les logs en temps réel
docker compose logs -f [service]

# Arrêter les services
docker compose down

# Reconstruire les images
docker compose build --no-cache

# Nettoyer les ressources inutilisées
docker system prune -f
docker volume prune -f

# Accéder à un conteneur
docker compose exec backend bash
```

### Bonnes pratiques
- Toujours utiliser `docker compose` (v2) et non `docker-compose`
- Vérifier les logs en cas d'erreur : `docker compose logs`
- Utiliser des volumes nommés pour les données persistantes
- Configurer les limites de ressources dans `docker-compose.override.yml` pour le développement

## 📝 Documentation

### Fichiers à maintenir
1. **`CHANGELOG.md`**
   - Suivre le format [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
   - Catégories : `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
   - Mettre à jour à chaque version

2. **`README.md`**
   - Description du projet
   - Prérequis et installation
   - Configuration
   - Démarrage rapide
   - Déploiement
   - Licence

3. **`TODO.md`**
   - Liste des tâches à faire
   - Classées par priorité et statut
   - Mise à jour quotidienne

4. **`ETAT_DU_PROJET.md`**
   - État d'avancement global
   - Blocages éventuels
   - Prochaines étapes
   - Mise à jour lors des réunions

### Documentation du code
- **Python** : docstrings Google style
  ```python
  def fonction_exemple(param1: str, param2: int) -> bool:
      """Brève description de la fonction.

      Args:
          param1: Description du premier paramètre.
          param2: Description du deuxième paramètre.

      Returns:
          Description de la valeur de retour.

      """
  ```
- **Frontend** : JSDoc pour les composants et fonctions
- **API** : Documentation OpenAPI via FastAPI
- **Bases de données** : Schémas et relations dans `/docs/database.md`

## 🧪 Tests

### Backend (Python)
```bash
# Lancer tous les tests
pytest

# Avec couverture de code
pytest --cov=app --cov-report=term-missing

# Lancer un test spécifique
pytest tests/path/to/test_file.py::test_function

# Vérifier le style de code
pylint app/
black --check app/
mypy app/
```

### Frontend (TypeScript/React)
```bash
# Lancer les tests
npm test

# Lancer les tests en mode watch
npm test -- --watch

# Vérifier le style de code
npm run lint

# Vérifier les types
tsc --noEmit
```

### Bonnes pratiques
- Couverture de code minimale : 80%
- Tester les cas limites et les erreurs
- Utiliser des fixtures pour les données de test
- Les tests doivent être isolés et reproductibles

## 🚀 Déploiement

### Environnements
1. **Développement (`development`)**
   - Local sur la machine du développeur
   - Base de données en mémoire ou locale
   - Mode debug activé
   - Logs détaillés

2. **Recette (`staging`)**
   - Reflète la production
   - Données de test
   - Utilisé pour les tests d'intégration
   - Accès limité

3. **Production (`production`)**
   - Environnement client
   - Données réelles
   - Haute disponibilité
   - Monitoring actif

### Gestion des configurations
- Utiliser des variables d'environnement pour toute configuration
- Fichier `.env` pour le développement local (ne pas le versionner)
- Fichier `.env.example` avec des valeurs par défaut (versionné)
- Pour la production, utiliser un gestionnaire de secrets (Vault, AWS Secrets Manager, etc.)

### Procédure de déploiement
1. Mettre à jour le numéro de version dans `pyproject.toml`
2. Mettre à jour `CHANGELOG.md`
3. Créer un tag Git : `git tag -a v1.0.0 -m "Version 1.0.0"`
4. Pousser les changements et le tag : `git push --follow-tags`
5. Le CI/CD se charge du déploiement

## 🔒 Sécurité

### Gestion des secrets
- **À FAIRE** :
  - Utiliser des variables d'environnement pour les secrets
  - Ne jamais commettre de clés API ou mots de passe
  - Utiliser un gestionnaire de secrets sécurisé en production
  - Régénérer toutes les clés lors du déploiement en production

- **À ÉVITER** :
  - Stocker des secrets dans le code source
  - Utiliser des valeurs par défaut pour les secrets
  - Utiliser le même secret entre les environnements

### Sécurité des dépendances
- Vérifier les vulnérabilités connues :
  ```bash
  # Python
  pip-audit
  safety check

  # Node.js
  npm audit
  npx snyk test
  ```
- Mettre à jour régulièrement les dépendances
- Épingler les versions exactes en production
- Vérifier les licences des dépendances

### Bonnes pratiques
- Validation des entrées utilisateur
- Protection contre les attaques CSRF et XSS
- Limitation du taux de requêtes
- Journalisation des activités sensibles
- Authentification à deux facteurs pour les comptes privilégiés

## 📅 Réunions et Suivi

### Daily (15 minutes max)
- Chaque jour ouvré à 9h30
- Tour de table :
  1. Ce qui a été fait hier
  2. Objectifs du jour
  3. Blocages éventuels
- Mettre à jour `ETAT_DU_PROJET.md`
- Mettre à jour le tableau de bord des tâches

### Revue de sprint (1h)
- Tous les 15 jours le vendredi à 14h
- Présenter les fonctionnalités terminées
- Vérifier les objectifs du sprint
- Préparer la démo pour le client
- Mettre à jour la documentation

### Rétrospective (1h)
- À la fin de chaque sprint
- Ce qui a bien fonctionné
- Points à améliorer
- Actions concrètes pour le prochain sprint
- Mettre à jour le plan d'action

### Outils de suivi
- Tableau Kanban pour les tâches
- Tableau de bord des métriques
- Documentation à jour dans le dépôt
- Mises à jour régulières de `ETAT_DU_PROJET.md`

## 📞 Support et Maintenance

### Support technique
- **Problèmes mineurs** : Créer une issue sur le dépôt Git
- **Problèmes urgents** : Contacter l'équipe sur le canal dédié
- **Demandes d'évolution** : Créer une issue avec le label `enhancement`
- **Bugs** : Créer une issue avec le label `bug` et les étapes pour reproduire

### Maintenance
- **Mises à jour de sécurité** : Appliquer dès que possible
- **Mises à jour mineures** : Planifier mensuellement
- **Mises à jour majeures** : Planifier trimestriellement
- **Sauvegardes** : Vérifier régulièrement les sauvegardes de la base de données

### Procédure d'urgence
1. Évaluer la gravité de l'incident
2. Si critique, appliquer un correctif immédiat
3. Communiquer avec les parties prenantes
4. Documenter l'incident et les actions correctives
5. Mettre en place des mesures préventives

---

## 📋 Checklist de sortie

Avant de terminer une tâche, vérifier :
- [ ] Tous les tests passent
- [ ] La couverture de code est suffisante
- [ ] La documentation est à jour
- [ ] Le code a été relu
- [ ] Les changements sont documentés dans `CHANGELOG.md`
- [ ] `ETAT_DU_PROJET.md` est à jour
- [ ] Les dépendances sont à jour et sécurisées

## 📜 Licence

Ce projet est sous licence [MIT](LICENSE).

---
*Dernière mise à jour : 20/06/2025 - [Consulter l'historique des modifications](CHANGELOG.md)*
