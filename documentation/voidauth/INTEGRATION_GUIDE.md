# Guide d'Intégration de VoidAuth

## Configuration de Base

### Backend (.env)
```env
VOIDAUTH_SERVER_URL=http://localhost:8080
VOIDAUTH_REALM=audionexus
VOIDAUTH_CLIENT_ID=audionexus-backend
VOIDAUTH_CLIENT_SECRET=votre-secret
VOIDAUTH_ADMIN_USER=admin
VOIDAUTH_ADMIN_PASSWORD=votre-mdp
VOIDAUTH_VERIFY_SSL=False
```

### Frontend (.env)
```env
VITE_OIDC_CLIENT_ID=audionexus-frontend
VITE_OIDC_AUTHORITY=http://localhost:8080/realms/audionexus
VITE_OIDC_REDIRECT_URI=http://localhost:3000/auth/callback
```

## Utilisation

### Initialisation
```python
from app.integrations.voidauth.factory import get_voidauth_client
voidauth = get_voidauth_client()
```

### Authentification
```python
# Login
tokens = voidauth.auth.authenticate_user(username, password)

# Vérification token
user_info = voidauth.auth.get_user_info(access_token)

# Rafraîchissement
new_tokens = voidauth.auth.refresh_token(refresh_token)
```

### Gestion Utilisateurs
```python
# Création
user_id = voidauth.users.create_user({
    'username': 'user',
    'email': 'user@example.com',
    'password': 'secure',
    'enabled': True
})

# Récupération
user = voidauth.users.get_user(user_id)

# Mise à jour
voidauth.users.update_user(user_id, {'firstName': 'John'})

# Suppression
voidauth.users.delete_user(user_id)
```

## Protection des Routes

### Décorateur de rôle
```python
from app.integrations.voidauth.decorators import requires_roles

@app.get("/admin")
@requires_roles(["admin"])
async def admin_route():
    return {"message": "Accès admin"}
```

## Dépannage

### Erreurs courantes
1. **Connexion échouée**
   - Vérifiez les logs du serveur
   - Vérifiez les identifiants

2. **Problèmes CORS**
   - Vérifiez les origines autorisées
   - Vérifiez la configuration CORS

3. **Tokens invalides**
   - Vérifiez les durées d'expiration
   - Vérifiez la signature des tokens

## Sécurité
- Activez HTTPS en production
- Restreignez les origines autorisées
- Utilisez des secrets forts
- Activez la vérification email
- Activez le 2FA

## Compatibilité VoidAuth v4.x
### Changements depuis v3.x
- API des tokens légèrement modifiée (mais compatible avec python-keycloak >= 5.x)
- Améliorations des scopes OpenID Connect
- Support renforcé des refresh tokens
- Sécurité SSL renforcée par défaut

### Mise à jour recommandée
```bash
pip install --upgrade python-keycloak>=5.7.0
```

### Fonctionnalités v4.x supportées
- ✅ Authentification utilisateur (password grant)
- ✅ Gestion des utilisateurs et rôles
- ✅ Refresh tokens avec validation
- ✅ Introspection des tokens
- ✅ Clients OAuth2 confidentiels
- ✅ Scopes personnalisés
- ✅ Multi-factor authentication (MFA)

### Test de compatibilité
```python
# Test de connexion basique v4.x
import keycloak
from keycloak import KeycloakOpenID

# Initialisation avec nouveaux paramètres v4.x
keycloak_openid = KeycloakOpenID(
    server_url="https://your-voidauth-server",
    client_id="your-client",
    realm_name="your-realm",
    client_secret_key="your-secret"
)
```
