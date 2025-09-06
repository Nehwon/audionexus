# Intégration de VoidAuth avec AudioNexus

Ce document explique comment configurer et utiliser VoidAuth comme système d'authentification pour AudioNexus.

## Prérequis

- Une instance VoidAuth en cours d'exécution (par défaut sur http://localhost:8080)
- Un client configuré dans VoidAuth pour AudioNexus
- Les identifiants d'administration de VoidAuth

## Configuration

1. **Variables d'environnement**

   Ajoutez les variables suivantes à votre fichier `.env` :

   ```
   # Configuration VoidAuth
   VOIDAUTH_SERVER_URL=http://localhost:8080
   VOIDAUTH_REALM=audionexus
   VOIDAUTH_CLIENT_ID=audionexus-backend
   VOIDAUTH_CLIENT_SECRET=votre_client_secret
   VOIDAUTH_ADMIN_USER=admin
   VOIDAUTH_ADMIN_PASSWORD=votre_mot_de_passe_admin
   ```

2. **Configuration CORS**

   Assurez-vous que les origines CORS sont correctement configurées dans `config.py` pour autoriser les requêtes depuis votre frontend et VoidAuth.

## Points d'API

### Connexion (Login)

```
POST /auth/login
```

**Paramètres :**
- `username` (string, requis) : Nom d'utilisateur
- `password` (string, requis) : Mot de passe

**Réponse :**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIg...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCIg..."
}
```

### Inscription (Register)

```
POST /auth/register
```

**Corps de la requête :**
```json
{
  "username": "nouvel_utilisateur",
  "email": "utilisateur@example.com",
  "password": "motdepasse",
  "full_name": "Prénom Nom"
}
```

**Réponse :**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "nouvel_utilisateur",
  "email": "utilisateur@example.com",
  "is_active": true,
  "is_superuser": false
}
```

### Récupérer l'utilisateur connecté

```
GET /auth/me
```

**En-têtes :**
```
Authorization: Bearer <access_token>
```

**Réponse :**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "utilisateur",
  "email": "utilisateur@example.com",
  "is_active": true,
  "is_superuser": false
}
```

## Protection des routes

Pour protéger une route et s'assurer que l'utilisateur est authentifié :

```python
from fastapi import Depends
from app.core.security.voidauth import get_current_user, has_role

@app.get("/protected-route")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": "Accès autorisé"}
```

Pour exiger un rôle spécifique :

```python
@app.get("/admin-route")
async def admin_route(_ = Depends(has_role(["admin"]))):
    return {"message": "Accès admin autorisé"}
```

## Configuration de VoidAuth

1. Créez un nouveau royaume (realm) pour AudioNexus
2. Créez un client avec les paramètres suivants :
   - Client ID : `audionexus-backend`
   - Client Protocol : `openid-connect`
   - Access Type : `confidential`
   - Valid Redirect URIs : `http://localhost:3000/*` (ajoutez vos URLs de production)
   - Web Origins : `*` (à restreindre en production)
3. Activez les fonctionnalités nécessaires :
   - Registration : `ON`
   - Login with email : `ON`
   - Forgot Password : `ON`
   - Remember Me : `ON`
   - Verify Email : `ON`

## Dépannage

### Erreurs de connexion
- Vérifiez que le serveur VoidAuth est en cours d'exécution
- Vérifiez que les identifiants du client sont corrects
- Vérifiez que les URLs de redirection sont correctement configurées

### Problèmes de CORS
- Vérifiez que les origines sont correctement configurées dans `config.py`
- Assurez-vous que le frontend et le backend sont sur les mêmes domaines ou que CORS est correctement configuré

### Problèmes de certificats SSL
- En développement, vous pouvez désactiver la vérification SSL en modifiant `verify=False` dans `voidauth_service.py`
- En production, utilisez toujours des certificats valides

## Sécurité et Protections Avancées

### Améliorations Récentes (v0.6.0)

AudioNexus inclut maintenant plusieurs couches de protection supplémentaires pour renforcer la sécurité :

#### 1. Validation Pydantic v2 Mise à Jour
- Validation améliorée des modèles de données utilisateur
- Protection contre l'injection de données malformées
- Gestion sécurisée des erreurs de validation

#### 2. Gestion des Sessions Renforcée
- Session manager unifié pour éviter les fuites de mémoire
- Déconnexion automatique des sessions inactives
- Protection contre les attaques de détournement de session

#### 3. Contrôles d'Accès Strictes
- Validation des rôles et permissions au niveau des endpoints
- Protection contre les escalades de privilèges
- Logs détaillés des tentatives d'accès non autorisées

#### 4. Chiffrement et Hachage Renforcés
- Utilisation exclusive de bcrypt/Argon2 pour le hachage des mots de passe
- Tokens JWT signés avec algorithmes sécurisés
- Rotation automatique des clés de sécurité

### Protection des Routes

Nouvelles améliorations de sécurité pour la protection des routes :

```python
from fastapi import Depends, HTTPException
from app.api.deps import get_current_active_user
from app.core.security import verify_user_permissions

@app.post("/api/sensitive-data")
async def sensitive_operation(
    data: SensitiveData,
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(verify_user_permissions(["admin", "editor"]))
):
    """
    Route protégée avec vérifications multiples :
    - Authentification requise
    - Utilisateur actif
    - Permissions spécifiques
    - Validation des données d'entrée
    """
    if not await verify_user_permissions(current_user, ["admin", "editor"]):
        raise HTTPException(
            status_code=403,
            detail="Permissions insuffisantes"
        )

    # Traitement sécurisé des données
    return await process_secure_data(data, current_user)
```

### Journalisation de Sécurité

Toutes les opérations sensibles sont désormais tracées :

```python
from app.core.logging import get_security_logger

security_logger = get_security_logger()

@router.post("/auth/register")
async def register_user(user_data: UserCreate, request: Request):
    try:
        new_user = await create_user(user_data)
        security_logger.info(
            f"New user registration: {new_user.id}",
            extra={
                "user_id": new_user.id,
                "ip_address": request.client.host,
                "user_agent": request.headers.get("User-Agent")
            }
        )
        return new_user
    except Exception as e:
        security_logger.warning(
            f"Registration failed: {str(e)}",
            extra={
                "email": user_data.email,
                "ip_address": request.client.host,
                "error": str(e)
            }
        )
        raise
```

### Vérification de Sécurité Régulière

Pour maintenir la sécurité optimale :

1. **Audit des logs de sécurité** hebdomadairement
2. **Mise à jour des dépendances** dès que des vulnérabilités sont découvertes
3. **Tests de pénétration** trimestriels
4. **Rotations des clés** à chaque déploiement majeur

### Configuration de Production Recommandée

```bash
# Variables de sécurité essentielles
JWT_SECRET_KEY=une_clé_très_longue_et_aléatoire_de_64_caractères_min
VOIDAUTH_CLIENT_SECRET=un_secret_client_unique_et_complexe
ENCRYPTION_KEY=clef_pour_chiffrement_symétrique_si_utilisé

# Headers de sécurité renforcés
SECURE_HEADERS=true
HSTS_HEADERS=true
CSP_HEADERS=strict
```

Cette configuration assure une protection complète contre les vulnérabilités communes tout en maintenant la performance de l'application.
