# Documentation de l'API AudioNexus

Cette documentation décrit l'API REST d'AudioNexus, qui permet d'interagir avec la plateforme de manière programmatique.

## Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification. Incluez le token dans l'en-tête `Authorization` des requêtes :

```
Authorization: Bearer votre_token_jwt
```

### Obtenir un Token d'Accès

#### 1. Authentification avec JSON (Recommandé)

```http
POST /api/v1/auth/login/access-token
Content-Type: application/json

{
  "username": "votre_nom_utilisateur",
  "password": "votre_mot_de_passe"
}
```

#### 2. Authentification avec Formulaire (Compatibilité OAuth2)

```http
POST /api/v1/auth/login/access-token
Content-Type: application/x-www-form-urlencoded

username=votre_nom_utilisateur&password=votre_mot_de_passe
```

#### Réponse en cas de succès (200 OK)

```json
{
  "access_token": "votre_jwt_token",
  "token_type": "bearer"
}
```

### Créer un Compte

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "nouvel_utilisateur",
  "email": "utilisateur@example.com",
  "password": "mot_de_passe_securise",
  "full_name": "Prénom Nom"
}
```

### Tester un Token

```http
GET /api/v1/auth/login/test-token
Authorization: Bearer votre_jwt_token
```

## Points de Terminaison

### Utilisateurs

#### Obtenir le Profil de l'Utilisateur Connecté

```http
GET /api/users/me
```

#### Mettre à Jour le Profil

```http
PUT /api/users/me
Content-Type: application/json

{
  "full_name": "Nouveau Nom",
  "email": "nouvel@email.com"
}
```

### Livres

#### Lister les Livres

```http
GET /api/books
```

Paramètres de requête :
- `q` : Recherche par titre/auteur
- `page` : Numéro de page (par défaut : 1)
- `per_page` : Nombre d'éléments par page (par défaut : 20)

#### Obtenir un Livre par ID

```http
GET /api/books/{book_id}
```

#### Ajouter un Livre

```http
POST /api/books
Content-Type: multipart/form-data

{
  "title": "Titre du livre",
  "author": "Auteur du livre",
  "file": "fichier_audio.mp3"
}
```

### Lecture

#### Obtenir la Progression de Lecture

```http
GET /api/books/{book_id}/progress
```

#### Mettre à Jour la Progression

```http
POST /api/books/{book_id}/progress
Content-Type: application/json

{
  "position": 3600,
  "completed": false
}
```

## Codes de Réponse

- `200 OK` : Requête réussie
- `201 Created` : Ressource créée avec succès
- `400 Bad Request` : Données de requête invalides
- `401 Unauthorized` : Authentification requise
- `403 Forbidden` : Permissions insuffisantes
- `404 Not Found` : Ressource non trouvée
- `500 Internal Server Error` : Erreur serveur

## Pagination

Les réponses de liste sont paginées et incluent des métadonnées :

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

## Validation des Données

Les données sont validées selon les règles suivantes :

- Email : Doit être un email valide
- Mot de passe : Au moins 8 caractères, avec des chiffres et des lettres
- Titre du livre : Entre 1 et 255 caractères
- Position de lecture : Nombre entier positif

## Gestion des Erreurs

Les erreurs sont renvoyées au format JSON :

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

## Limites de Taux

L'API est limitée à 1000 requêtes par heure et par adresse IP. Les en-têtes de réponse incluent :

- `X-RateLimit-Limit` : Nombre total de requêtes autorisées
- `X-RateLimit-Remaining` : Nombre de requêtes restantes
- `X-RateLimit-Reset` : Timestamp de réinitialisation de la limite

## Exemple d'Utilisation avec cURL

```bash
# Authentification
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"votre_mot_de_passe"}' \
  | jq -r '.access_token')

# Obtenir la liste des livres
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/books
```

## SDK et Bibliothèques

Des bibliothèques client sont disponibles pour :

- Python : `pip install audionexus-client`
- JavaScript/TypeScript : `npm install audionexus-client`

## Support

Pour toute question concernant l'API, veuillez ouvrir une [issue](https://gitea.lamachere.fr/fabrice/AudioNexus/issues) ou nous contacter à api-support@audionexus.fr.
