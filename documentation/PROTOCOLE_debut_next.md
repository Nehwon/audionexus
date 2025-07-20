# Protocole de Reprise - Problèmes d'Authentification (21/07/2025)

## 📌 Contexte Actuel

### Problèmes en Cours
- Erreur 500 dans l'endpoint `/auth/register`
- Problème de validation Pydantic v2 avec `UserCreate`
- Gestion des sessions asynchrones à finaliser

### Fichiers Impactés
- `app/core/api/auth.py` - Endpoints d'authentification
- `app/db/models/base.py` - Modèles Pydantic
- `app/tests/test_auth.py` - Tests d'authentification

## 🔄 Étapes de Reprise

### 1. Préparation de l'Environnement

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -e ".[dev]"

# Vérifier que aiosqlite est installé
pip install aiosqlite
```

### 2. Vérification des Dépendances

Assurez-vous que les versions suivantes sont installées :
- FastAPI >= 0.100.0
- SQLAlchemy >= 2.0.0
- Pydantic >= 2.0.0
- python-jose[cryptography] >= 3.3.0
- passlib[bcrypt] >= 1.7.4

### 3. Configuration des Variables d'Environnement

Vérifiez que votre fichier `.env` contient :

```env
# Configuration de l'application
APP_ENV=development
DEBUG=true

# Base de données (SQLite pour les tests)
DATABASE_URL=sqlite+aiosqlite:///:memory:
TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:

# Sécurité
SECRET_KEY=votre_cle_secrete_tres_longue
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 🔧 Résolution des Problèmes Courants

### Problème : Erreur 500 sur `/auth/register`
**Symptôme** : 
```
TypeError: `TypeAdapter[typing.Annotated[ForwardRef("'UserCreate'"), Body(PydanticUndefined)]]` is not fully defined
```

**Solution** :
1. Vérifiez que `UserCreate` est correctement défini dans `app/db/models/base.py`
2. Assurez-vous que tous les modèles Pydantic utilisent la syntaxe v2
3. Ajoutez `model_config = ConfigDict(from_attributes=True)` si nécessaire

### Problème : Erreurs de Session
**Symptôme** : 
```
RuntimeError: Task <Task pending...> got Future <Future pending> attached to a different loop
```

**Solution** :
1. Vérifiez que vous utilisez `AsyncSession` partout
2. Utilisez `await` pour tous les appels asynchrones
3. Assurez-vous que les transactions sont correctement gérées avec `async with db.begin()`

## 🧪 Exécution des Tests

Pour exécuter uniquement les tests d'authentification :

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter les tests d'authentification
pytest app/tests/test_auth.py -v

# Pour exécuter un test spécifique
pytest app/tests/test_auth.py::test_register_user -v
```

## 📝 Prochaines Étapes

1. Résoudre l'erreur 500 sur `/auth/register`
2. Vérifier que tous les endpoints d'authentification fonctionnent
3. Mettre à jour la documentation des API
4. Ajouter des tests supplémentaires pour couvrir plus de cas d'utilisation

## 🔗 Ressources Utiles

- [Documentation FastAPI - Authentification](https://fastapi.tiangolo.com/tutorial/security/)
- [Guide de migration Pydantic v2](https://docs.pydantic.dev/latest/migration/)
- [SQLAlchemy 2.0 - AsyncIO](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
