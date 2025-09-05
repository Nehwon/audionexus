# CI/CD Pipelines - AudioNexus

Ce document décrit les pipelines d'intégration continue et de déploiement utilisés dans le projet AudioNexus.

## Workflows GitHub Actions

### Frontend CI (`frontend-ci.yml`)
**Déclenchement :** Push/PR sur `main` ou `develop` affectant le dossier `frontend/`

**Jobs :**
1. **frontend-test** : Tests unitaires, linting, build
2. **frontend-e2e** : Tests end-to-end avec Playwright
3. **frontend-deploy-staging** : Déploiement vers staging (branche `develop`)
4. **frontend-deploy-prod** : Déploiement vers production (branche `main`)

**Environnements de déploiement :**
- **Staging** : Firebase Hosting (`audionexus-staging`)
- **Production** : Firebase Hosting (`audionexus-prod`)

### Backend CI (`backend-ci.yml`)
**Déclenchement :** Push/PR sur `main` ou `develop` affectant le backend

**Jobs :**
1. **backend-test** : Tests avec MySQL/Redis, couverture de code
2. **backend-deploy-staging** : Déploiement ECS staging (branche `develop`)
3. **backend-deploy-prod** : Déploiement ECS production (branche `main`)

**Environnements de déploiement :**
- **Staging** : AWS ECS (`audionexus-staging`)
- **Production** : AWS ECS (`audionexus-prod`)

### Sécurité (`security-audit.yml`)
**Déclenchement :** Programmée (hebdomadaire) + push/PR

**Scans de sécurité :**
- **Frontend** : Audit npm, Snyk, CodeQL
- **Backend** : Bandit, Safety, Trivy
- **Docker** : Scan d'images avec Trivy

## Secrets requis

### Frontend
```bash
FIREBASE_TOKEN_STAGING     # Token Firebase pour staging
FIREBASE_TOKEN_PROD       # Token Firebase pour production
STAGING_API_URL          # URL API staging
PROD_API_URL            # URL API production
SNYK_TOKEN              # Token Snyk pour scan sécurité
```

### Backend
```bash
AWS_ACCESS_KEY_ID_STAGING     # Clés AWS staging
AWS_SECRET_ACCESS_KEY_STAGING
AWS_ACCESS_KEY_ID_PROD       # Clés AWS production
AWS_SECRET_ACCESS_KEY_PROD
AWS_REGION                   # Région AWS
```

## Variables d'environnement

### Build Frontend
- `VITE_API_BASE_URL` : URL de l'API
- `VITE_ENVIRONMENT` : environnement (staging/production)

## Déploiement

### Frontend
```bash
# Staging
firebase deploy --project audionexus-staging --only hosting

# Production
firebase deploy --project audionexus-prod --only hosting
```

### Backend
```bash
# Build image
docker build -t registry/image:tag .

# Deploy ECS
aws ecs update-service --cluster cluster --service service --force-new-deployment
```

## Monitoring et Alertes

- **Rapports de couverture** : Upload vers Codecov
- **Tests de sécurité** : Rapports SARIF vers GitHub Security
- **Notifications** : Commentaires automatiques sur les PR après déploiement
- **Artifacts** : Conservation 30 jours pour debug

## Branches et Environnements

- **`main`** : Production
- **`develop`** : Staging et développement
- **Pull Requests** : Tests complets sans déploiement

## Tests Locaux

### Frontend
```bash
cd frontend
npm run test:e2e  # Tests E2E
npm run test      # Tests unitaires
```

### Backend
```bash
pytest --cov=app  # Tests avec couverture
```

## Optimisations

- **Cache** : Dépendances npm pip cachées
- **Parallel** : Tests exécutés en parallèle
- **Matrix** : Tests multi-navigateurs pour E2E