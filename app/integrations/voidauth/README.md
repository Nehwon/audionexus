# Intégration VoidAuth

Ce module fournit une interface pour interagir avec un serveur VoidAuth (basé sur Keycloak) pour la gestion de l'authentification et des utilisateurs.

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Configuration VoidAuth
VOIDAUTH_SERVER_URL=http://localhost:8080
VOIDAUTH_REALM=audionexus
VOIDAUTH_CLIENT_ID=audionexus-backend
VOIDAUTH_CLIENT_SECRET=votre-client-secret
VOIDAUTH_ADMIN_USER=admin
VOIDAUTH_ADMIN_PASSWORD=votre-mot-de-passe-admin
VOIDAUTH_VERIFY_SSL=False  # Désactiver en développement
```

### Installation des dépendances

Assurez-vous d'avoir installé les dépendances requises :

```bash
pip install python-keycloak python-dotenv
```

## Utilisation

### Initialisation du client

```python
from app.integrations.voidauth.factory import get_voidauth_client

# Récupération du client VoidAuth
voidauth = get_voidauth_client()

if not voidauth or not voidauth.is_initialized():
    print("Erreur lors de l'initialisation de VoidAuth")
    exit(1)
```

### Authentification d'un utilisateur

```python
# Authentification d'un utilisateur
tokens = voidauth.auth.authenticate_user(
    username="utilisateur",
    password="motdepasse"
)

if tokens:
    print(f"Authentification réussie. Token: {tokens['access_token']}")
else:
    print("Échec de l'authentification")
```

### Gestion des utilisateurs

```python
# Création d'un nouvel utilisateur
user_id = voidauth.users.create_user({
    'username': 'nouvel_utilisateur',
    'email': 'utilisateur@example.com',
    'password': 'MotDePasseSecurise123!',
    'first_name': 'Prénom',
    'last_name': 'Nom',
    'enabled': True,
    'email_verified': True
})

if user_id:
    print(f"Utilisateur créé avec l'ID: {user_id}")
else:
    print("Échec de la création de l'utilisateur")
```

### Vérification d'un token

```python
# Vérification d'un token
user_info = voidauth.auth.get_user_info("votre.jwt.token.ici")
if user_info:
    print(f"Utilisateur connecté: {user_info['preferred_username']}")
else:
    print("Token invalide ou expiré")
```

## Gestion des erreurs

Le module définit plusieurs exceptions personnalisées que vous pouvez intercepter :

```python
from app.integrations.voidauth.exceptions import (
    VoidAuthError,
    VoidAuthAuthenticationError,
    VoidAuthUserNotFoundError
)

try:
    # Code qui interagit avec VoidAuth
    pass
except VoidAuthAuthenticationError as e:
    print(f"Erreur d'authentification: {str(e)}")
except VoidAuthUserNotFoundError as e:
    print(f"Utilisateur non trouvé: {str(e)}")
except VoidAuthError as e:
    print(f"Erreur VoidAuth: {str(e)}")
```

## Tests

Pour exécuter les tests d'intégration :

```bash
pytest tests/integration/test_voidauth_integration.py -v
```

## Sécurité

- Ne stockez jamais les identifiants d'administration dans le code source
- Utilisez toujours HTTPS en production
- Mettez à jour régulièrement les dépendances
- Limitez les permissions des utilisateurs au strict nécessaire
