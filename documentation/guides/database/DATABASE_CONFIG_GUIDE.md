# Guide de Configuration des Bases de Données AudioNexus

## Vue d'ensemble

AudioNexus utilise maintenant un système de configuration unifiée qui résoud définitivement les conflits entre SQLite (tests/développement) et MySQL (production).

## Architecture du Système

### Configuration Unifiée

Le système utilise `app/config.py` comme source unique de vérité :

- **En développement** : SQLite avec fichier local (`./audionexus_dev.db`)
- **En tests** : SQLite en mémoire pour l'isolation des tests
- **En production** : MySQL obligatoire pour les performances

### Basculement Automatique

La configuration détecte automatiquement l'environnement et ajuste la base de données :

```bash
# Développement (SQLite)
export ENVIRONMENT=development
./scripts/setup_env.sh dev

# Production (MySQL)
export ENVIRONMENT=production
./scripts/setup_env.sh prod

# Tests (SQLite en mémoire)
export TESTING=true
./run_tests.sh
```

## Configuration par Environnement

### Développement (`.env.development`)

```bash
ENVIRONMENT=development
DB_TYPE=sqlite
SQLITE_PATH=./audionexus_dev.db

# Clés de développement (pas pour la production !)
SECRET_KEY=dev-secret-key-change-me-in-production
```

### Production (`.env.production`)

```bash
ENVIRONMENT=production
DB_TYPE=mysql
DB_HOST=db
DB_USER=audionexus
DB_PASSWORD=YOUR_PRODUCTION_PASSWORD_HERE
DB_NAME=audionexus

# Clés de production (À CHANGER ABSOLUMENT !)
SECRET_KEY=YOUR_PRODUCTION_SECRET_KEY_HERE
```

## Commandes Essentielles

### Basculement d'Environnement

```bash
# Lister les environnements disponibles
./scripts/setup_env.sh list

# Bascule en développement
./scripts/setup_env.sh dev

# Bascule en production
./scripts/setup_env.sh prod

# Afficher la configuration actuelle
./scripts/setup_env.sh status
```

### Gestion des Migrations

```bash
# Créer une migration (fonctionne pour les deux SGBD)
alembic revision -m "Description de la modification"

# Appliquer les migrations (selon l'environnement configuré)
alembic upgrade head

# Retour arrière d'une migration
alembic downgrade -1

# Pour production MySQL, utiliser un environnement approprié
export ENVIRONMENT=production
alembic upgrade head
```

### Test de Connectivité MySQL

Avant de déployer en production, testez toujours la connectivité MySQL :

```bash
# Tester la connectivité MySQL
python scripts/test_mysql_connectivity.py

# Ou, si permissions d'exécution
./scripts/test_mysql_connectivity.py
```

Le script vérifie :
- Connexion à MySQL
- Version du serveur
- Permissions d'écriture
- Tables existantes

### Lancement des Tests

```bash
# Tests automatiques avec configuration SQLite
./run_tests.sh

# Tests avec couverture détaillée
pytest --cov=app --cov-report=html app/tests/
```

## Bonnes Pratiques

### 1. Respect des Environnements

- **Jamais de commits** avec des variables de production
- **Toujours utiliser** le système de basculement d'environnement
- **Tester les migrations** sur SQLite avant production MySQL

### 2. Gestion des Clés Secrètes

- Utiliser des valeurs différentes en dev/test/production
- Générer des clés longues et aléatoires pour la production
- Ne jamais committer de vraies clés de production

### 3. Modèles de Base de Données

Les modèles sont maintenant agnostiques du SGBD :

```python
# ✅ BON - Compatible SQLite et MySQL
name = Column(String(100), nullable=False, index=True)

# ❌ MAUVAIS - Spécifique MySQL
name = Column(String(100, charset='utf8mb4'), nullable=False)
```

### 4. Migrations Alembic

- Toujours tester les migrations sur SQLite d'abord
- Créer des migrations réversibles quand possible
- Documenter les changements de schéma dans les messages

### 5. Variables d'Environnement

Préférer la configuration via les fichiers `.env.*` plutôt que les variables système directes :

```bash
# ✅ BON
echo "DB_PASSWORD=ma_super_motdepasse" >> .env.production

# ❌ MAUVAIS
export DB_PASSWORD=ma_super_motdepasse
```

## Dépannage

### Problème : Migrations qui échouent

```bash
# Vérifier la configuration actuelle
./scripts/setup_env.sh status

# Recréer la base de test si nécessaire
rm -f audionexus_dev.db
alembic upgrade head

# Pour MySQL, vérifier la connectivité d'abord
python scripts/test_mysql_connectivity.py

# Si problème de schéma, vérifier l'encodage MySQL
mysql -u audionexus -p -e "SHOW CREATE DATABASE audionexus;"
```

### Problème : Tests qui échouent à cause de la DB

```bash
# Forcer la configuration de test
export TESTING=true
./run_tests.sh
```

### Problème : Configuration non prise en compte

```bash
# Vérifier que le .env est bien chargé
python -c "from app.config import settings; print(settings.database.type)"

# Recharger manuellement
unset ENVIRONMENT; source .env
```

## Migration depuis l'Ancien Système

L'ancien système avec les classes `Config`, `TestingConfig`, etc. a été supprimé.
Si vous aviez des configurations personnalisées, migrez vers :

```python
# Ancien système (obsolète)
class MyConfig(Config):
    CUSTOM_VAR = "value"

# Nouveau système (recommandé)
from app.config import settings

# Accéder via settings.custom_var
# La configuration est maintenant centralisée dans .env.*
```

## Support et Évolution

Ce système est conçu pour être :
- **Évolutif** : Ajout facile de nouveaux SGBD (PostgreSQL, etc.)
- **Maintenable** : Configuration centralisée et documentée
- **Sécurisé** : Séparation claire des environnements

Pour toute question ou évolution, consultez le fichier `app/config.py` et les scripts dans `scripts/`.