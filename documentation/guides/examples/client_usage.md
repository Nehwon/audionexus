# Exemples d'Utilisation Client AudioNexus

Ce guide présente des exemples pratiques d'utilisation de l'API AudioNexus pour les développeurs.

## Prérequis

```bash
pip install requests python-jose aiohttp
```

## 1. Authentification VoidAuth

### Connexion et obtention de tokens

```python
import requests
from typing import Dict, Optional

class AudioNexusClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def login(self, username: str, password: str) -> Dict:
        """Authentification via VoidAuth."""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]

        # Configurer les headers pour les futures requêtes
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })

        return data

    def refresh_access_token(self) -> str:
        """Rafraîchir le token d'accès."""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]

        # Mettre à jour le header d'autorisation
        self.session.headers["Authorization"] = f"Bearer {self.access_token}"

        return self.access_token

# Utilisation
client = AudioNexusClient()
client.login("votre_username", "votre_password")
print(f"Connecté avec token: {client.access_token[:20]}...")
```

## 2. Gestion des Instances Audiobookshelf

### Configuration d'une nouvelle instance

```python
def setup_audiobookshelf_instance(client: AudioNexusClient, instance_config: Dict) -> Dict:
    """Créer et configurer une instance Audiobookshelf."""

    # Créer l'instance
    response = client.session.post(
        f"{client.base_url}/api/v1/audiobookshelf/instances",
        json={
            "name": instance_config["name"],
            "base_url": instance_config["base_url"],
            "username": instance_config["username"],
            "password": instance_config["password"]
        }
    )
    response.raise_for_status()
    instance = response.json()

    print(f"Instance créée: {instance['id']} - {instance['name']}")

    # Tester la connexion
    test_response = client.session.post(
        f"{client.base_url}/api/v1/audiobookshelf/instances/{instance['id']}/test"
    )
    test_result = test_response.json()

    print(f"Statut de connexion: {test_result['status']}")
    print(f"Version Audiobookshelf: {test_result.get('version', 'N/A')}")

    return instance

# Exemple d'utilisation
instance_config = {
    "name": "Ma Bibliothèque Audio",
    "base_url": "https://audiobooks.mondomaine.com",
    "username": "admin",
    "password": "mot_de_passe_sécurisé"
}

instance = setup_audiobookshelf_instance(client, instance_config)
```

### Rotation des tokens de sécurité

```python
def rotate_instance_token(client: AudioNexusClient, instance_id: int, new_password: str) -> Dict:
    """Effectuer une rotation du token d'une instance."""

    response = client.session.put(
        f"{client.base_url}/api/v1/audiobookshelf/instances/{instance_id}/rotate-token",
        json={"password": new_password}
    )
    response.raise_for_status()

    updated_instance = response.json()
    print(f"Token rotaté pour l'instance {instance_id}")

    return updated_instance

# Utilisation sécurisée avec mot de passe temporaire
new_secure_password = "nouveau_mot_de_passe_très_sécurisé"
rotate_instance_token(client, instance["id"], new_secure_password)
```

## 3. Synchronisation Intelligente

### Synchronisation avec gestion des conflits

```python
def sync_with_conflict_resolution(client: AudioNexusClient, instance_id: int, strategy: str = "latest_wins") -> Dict:
    """Lancer une synchronisation avec stratégie de résolution des conflits."""

    response = client.session.post(
        f"{client.base_url}/api/v1/audiobookshelf/sync/instances/{instance_id}/sync",
        json={
            "full_sync": False,
            "conflict_strategy": strategy
        }
    )
    response.raise_for_status()

    sync_result = response.json()
    print("Synchronisation lancée:"    print(f"  - Type: {sync_result.get('sync_type', 'N/A')}")
    print(f"  - Instance: {sync_result.get('instance_name', 'N/A')}")

    return sync_result

# Stratégies disponibles:
# - "latest_wins": Priorité aux données les plus récentes
# - "manual": Intervention manuelle requise
# - "merge": Fusion intelligente des données

sync_with_conflict_resolution(client, instance["id"], "latest_wins")
```

### Synchronisation de toutes les instances

```python
def sync_all_instances(client: AudioNexusClient) -> Dict:
    """Synchroniser toutes les instances actives."""

    response = client.session.post(
        f"{client.base_url}/api/v1/audiobookshelf/sync/sync-all",
        json={"full_sync": True}
    )
    response.raise_for_status()

    result = response.json()
    print("Synchronisation globale lancée pour toutes les instances")

    return result

sync_all_instances(client)
```

## 4. Gestion Avancée des Données

### Recherche et filtrage d'audiobooks

```python
def search_audiobooks(client: AudioNexusClient, query: str, filters: Dict = None) -> List[Dict]:
    """Rechercher des livres audio avec filtres avancés."""

    search_params = {"q": query}

    if filters:
        search_params.update(filters)

    response = client.session.get(
        f"{client.base_url}/api/v1/audiobooks",
        params=search_params
    )
    response.raise_for_status()

    return response.json()

# Recherche avec filtres
results = search_audiobooks(
    client,
    "science fiction",
    {
        "author": "Isaac Asimov",
        "genre": "Science Fiction",
        "min_rating": 4.0
    }
)

for book in results[:5]:  # Afficher les 5 premiers résultats
    print(f"- {book['title']} par {', '.join(book.get('authors', ['Auteur inconnu']))}")
```

### Gestion des conflits de synchronisation

```python
def get_sync_conflicts(client: AudioNexusClient) -> List[Dict]:
    """Récupérer les conflits de synchronisation nécessitant une résolution manuelle."""

    response = client.session.get(f"{client.base_url}/api/v1/audiobookshelf/sync/conflicts")
    response.raise_for_status()

    conflicts = response.json()
    print(f"Conflits détectés: {len(conflicts)}")

    return conflicts

def resolve_conflict(client: AudioNexusClient, conflict_id: str, resolution: str, data: Dict) -> Dict:
    """Résoudre un conflit spécifique."""

    response = client.session.put(
        f"{client.base_url}/api/v1/audiobookshelf/sync/conflicts/{conflict_id}/resolve",
        json={
            "resolution": resolution,
            "data": data
        }
    )
    response.raise_for_status()

    return response.json()

# Vérifier et résoudre les conflits
conflicts = get_sync_conflicts(client)

for conflict in conflicts:
    if conflict["type"] == "duplicate_book":
        # Fusionner les métadonnées
        resolution_data = {
            "merge_authors": True,
            "keep_highest_rating": True
        }
        resolve_conflict(client, conflict["id"], "merge", resolution_data)
```

## 5. Monitoring et Métriques

### Suivi du statut des instances

```python
def get_instance_metrics(client: AudioNexusClient, instance_id: int) -> Dict:
    """Récupérer les métriques détaillées d'une instance."""

    response = client.session.get(
        f"{client.base_url}/api/v1/audiobookshelf/sync/instances/{instance_id}/progress"
    )
    response.raise_for_status()

    metrics = response.json()
    print("=== Métriques d'instance ==="    print(f"Nom: {metrics['name']}")
    print(f"Livres synchronisés: {metrics['synced_audiobooks']}")
    print(f"Dernière synchro: {metrics.get('last_sync', 'Jamais')}")
    print(f"Statut: {metrics['status']}")

    if metrics.get('last_error'):
        print(f"Dernière erreur: {metrics['last_error']}")

    return metrics

get_instance_metrics(client, instance["id"])
```

### État général du système

```python
def get_system_health(client: AudioNexusClient) -> Dict:
    """Vérifier l'état général du système."""

    response = client.session.get(f"{client.base_url}/api/v1/health")
    response.raise_for_status()

    health = response.json()
    print(f"Statut système: {health.get('status', 'Inconnu')}")
    print(f"Base de données: {health.get('database', 'Inconnu')}")
    print(f"Cache: {health.get('cache', 'Inconnu')}")

    return health

get_system_health(client)
```

## 6. Gestion d'Erreurs et Robustesse

### Gestion des erreurs avec retry automatique

```python
import time
from requests.exceptions import RequestException, Timeout

def api_call_with_retry(client: AudioNexusClient, method: str, url: str,
                       max_retries: int = 3, **kwargs) -> requests.Response:
    """Appel API avec mécanisme de retry automatique."""

    for attempt in range(max_retries):
        try:
            response = client.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        except (RequestException, Timeout) as e:
            if attempt == max_retries - 1:
                raise e

            # Retry avec backoff exponentiel
            wait_time = 2 ** attempt
            print(f"Tentative {attempt + 1} échouée, retry dans {wait_time}s: {str(e)}")
            time.sleep(wait_time)

        except Exception as e:
            # Erreurs non-retryables
            raise e

# Utilisation
try:
    response = api_call_with_retry(client, "GET",
                                  f"{client.base_url}/api/v1/audiobookshelf/instances")
    instances = response.json()
except Exception as e:
    print(f"Impossible de récupérer les instances: {e}")
```

## 7. Exemple Complet d'Intégration

```python
def main():
    """Exemple complet d'intégration AudioNexus."""

    # Initialisation
    client = AudioNexusClient("https://audio-api.mondomaine.com")

    try:
        # Authentification
        client.login("admin", "secure_password")

        # Configuration d'instance
        instance_config = {
            "name": "Bibliothèque Principale",
            "base_url": "https://audiobooks.mondomaine.com",
            "username": "audiobookshelf_user",
            "password": "audiobookshelf_secure_password"
        }

        instance = setup_audiobookshelf_instance(client, instance_config)

        # Synchronisation initiale complète
        print("Lancement synchronisation initiale...")
        sync_result = sync_with_conflict_resolution(client, instance["id"], "latest_wins")

        # Attendre la fin de la synchronisation (dans un vrai cas, utiliser un système de jobs)
        time.sleep(10)

        # Vérifier le statut
        metrics = get_instance_metrics(client, instance["id"])

        # Recherche de contenu
        books = search_audiobooks(client, "mystère", {"min_rating": 4.0})

        print(f"Recherche trouvée {len(books)} livres")

        # Vérifier les conflits
        conflicts = get_sync_conflicts(client)
        if conflicts:
            print(f"⚠️ {len(conflicts)} conflits nécessitent une résolution")

    except Exception as e:
        print(f"Erreur lors de l'exécution: {e}")
        return False

    print("✅ Intégration AudioNexus terminée avec succès")
    return True

if __name__ == "__main__":
    main()
```

## Références API

### Endpoints Principaux
- `POST /api/v1/auth/login` - Authentification
- `GET /api/v1/audiobookshelf/instances` - Liste des instances
- `POST /api/v1/audiobookshelf/instances` - Créer une instance
- `POST /api/v1/audiobookshelf/sync/sync-all` - Synchronisation globale

### Codes de Statut
- `200`: Succès
- `401`: Non autorisé (token expiré)
- `422`: Données invalides
- `429`: Rate limiting
- `500`: Erreur serveur

Pour la documentation API complète, consultez: `http://localhost:8000/docs`
