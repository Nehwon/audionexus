# Tests pour AudioNexus

Ce répertoire contient les tests automatisés pour l'application AudioNexus.

## Structure des dossiers

```
tests/
├── __init__.py
├── conftest.py           # Configuration des fixtures partagées
├── test_api/             # Tests d'API
│   ├── __init__.py
│   ├── test_auth.py      # Tests d'authentification
│   └── test_health.py    # Tests de santé
├── test_models/          # Tests des modèles
│   ├── __init__.py
│   └── test_user.py      # Tests du modèle User
└── test_services/        # Tests des services
    ├── __init__.py
    └── test_auth.py      # Tests des services d'authentification
```

## Exécution des tests

### Prérequis

- Python 3.11+
- Toutes les dépendances de développement (voir `requirements-dev.txt`)

### Commandes utiles

Exécuter tous les tests :
```bash
pytest
```

Exécuter les tests avec couverture de code :
```bash
pytest --cov=app --cov-report=term-missing
```

Exécuter uniquement les tests unitaires :
```bash
pytest -m "unit"
```

Exécuter uniquement les tests d'intégration :
```bash
pytest -m "integration"
```

Générer un rapport de couverture HTML :
```bash
pytest --cov=app --cov-report=html
```

## Écrire de nouveaux tests

### Conventions

- Nommez les fichiers de test avec le préfixe `test_`
- Utilisez des noms de fonctions descriptifs commençant par `test_`
- Groupez les tests liés dans des classes
- Utilisez les marqueurs pytest (`@pytest.mark`) pour catégoriser les tests

### Exemple de test

```python
def test_user_creation(db_session):
    """Teste la création d'un utilisateur."""
    user = User(username="test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == "test"
```

## Fixtures disponibles

Voir `conftest.py` pour la liste complète des fixtures disponibles. Voici les principales :

- `app`: Instance de l'application Flask pour les tests
- `db`: Connexion à la base de données de test
- `db_session`: Session de base de données pour les tests
- `client`: Client de test pour les requêtes HTTP
- `test_user`: Utilisateur de test avec le rôle 'user'
- `admin_user`: Utilisateur de test avec le rôle 'admin'
- `test_token`: Token JWT valide pour l'utilisateur de test
- `admin_token`: Token JWT valide pour l'admin
- `authenticated_client`: Client de test authentifié
- `authenticated_admin_client`: Client de test authentifié en tant qu'admin

## Tests d'intégration

Les tests marqués avec `@pytest.mark.integration` sont des tests d'intégration qui peuvent nécessiter des services externes. 
Ils sont exclus par défaut. Pour les exécuter :

```bash
pytest -m "integration"
```

## Débogage

Pour activer la sortie de débogage :

```bash
pytest -vvs
```

Pour exécuter un test spécifique :

```bash
pytest tests/test_models/test_user.py::test_user_creation -v
```

## Couverture de code

La couverture de code est surveillée via `pytest-cov`. Le seuil minimum est défini à 80% dans `pytest.ini`.

Pour générer un rapport de couverture :

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # Sur macOS/Linux
```

## Bonnes pratiques

- Écrivez des tests indépendants
- Utilisez des fixtures pour la configuration commune
- Ne testez pas la logique de Flask ou des bibliothèques externes
- Vérifiez à la fois les cas de succès et d'échec
- Utilisez des données de test réalistes mais simples
- Gardez les tests rapides et isolés
- Nommez clairement les tests pour qu'ils servent de documentation
