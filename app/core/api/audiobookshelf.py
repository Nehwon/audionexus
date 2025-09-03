"""
Client pour l'API Audiobookshelf.
Documentation complète de l'API : https://api-docs.audiobookshelf.org/
"""
import os
import json
import requests
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from urllib.parse import urljoin

class AudiobookshelfClient:
    """Client pour interagir avec l'API d'Audiobookshelf."""

    def __init__(self, base_url: str, token: str):
        """Initialise le client avec un token d'authentification existant.

        Args:
            base_url: URL de base du serveur Audiobookshelf (ex: 'http://localhost:13378')
            token: Token JWT d'authentification
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.token = token
        self.user = None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Effectue une requête HTTP vers l'API.
        
        Args:
            method: Méthode HTTP (get, post, put, delete)
            endpoint: Point de terminaison de l'API (sans le préfixe /api)
            **kwargs: Arguments supplémentaires pour la requête
            
        Returns:
            Réponse JSON décodée
        """
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        headers = kwargs.pop('headers', {})
        
        # Ajouter le token d'authentification si disponible
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            **kwargs
        )
        
        # Gérer les erreurs HTTP
        response.raise_for_status()
        
        # Essayer de parser la réponse JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"status": "success", "message": "No content"}
    
    def authenticate(self, username: str, password: str) -> None:
        """Authentifie l'utilisateur et stocke le token."""
        endpoint = "auth/login"
        data = {
            "username": username,
            "password": password
        }

        # Fait une requête sans token pour l'authentification
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        response = requests.post(url, json=data, timeout=30)

        if response.status_code == 200:
            response_data = response.json()
            self.token = response_data.get('user', {}).get('token')
            self.user = response_data.get('user')
        else:
            raise Exception(f"Authentication failed: HTTP {response.status_code}")

    @classmethod
    def from_credentials(cls, base_url: str, username: str, password: str) -> 'AudiobookshelfClient':
        """Crée un client en s'authentifiant avec nom d'utilisateur et mot de passe.

        Args:
            base_url: URL de base du serveur
            username: Nom d'utilisateur
            password: Mot de passe

        Returns:
            Instance du client authentifiée
        """
        client = cls(base_url, "")
        client.authenticate(username, password)
        return client
    
    # Méthodes pour les bibliothèques
    def get_libraries(self) -> List[Dict]:
        """Récupère la liste des bibliothèques."""
        return self._make_request('get', 'libraries')
    
    def get_library(self, library_id: str) -> Dict:
        """Récupère les détails d'une bibliothèque."""
        return self._make_request('get', f'libraries/{library_id}')
    
    # Méthodes pour les livres audio
    def get_recently_added(self, limit: int = 10) -> List[Dict]:
        """Récupère les livres audio récemment ajoutés."""
        return self._make_request('get', f'items/recently-added?limit={limit}')
    
    def get_audiobook(self, item_id: str) -> Dict:
        """Récupère les détails d'un livre audio."""
        return self._make_request('get', f'items/{item_id}')
    
    def search_library(self, library_id: str, query: str) -> Dict:
        """Recherche dans une bibliothèque."""
        return self._make_request('get', f'libraries/{library_id}/search?q={query}')
    
    # Méthodes pour les collections
    def get_collections(self) -> List[Dict]:
        """Récupère la liste des collections."""
        return self._make_request('get', 'collections')
    
    # Méthodes pour les utilisateurs (admin uniquement)
    def get_users(self) -> List[Dict]:
        """Récupère la liste des utilisateurs (admin uniquement)."""
        return self._make_request('get', 'users')
    
    # Méthodes pour les fichiers multimédias
    def upload_audiobook(self, library_id: str, file_path: str, metadata: Optional[Dict] = None) -> Dict:
        """Télécharge un nouveau livre audio.
        
        Args:
            library_id: ID de la bibliothèque cible
            file_path: Chemin vers le fichier à téléverser
            metadata: Métadonnées optionnelles pour le livre
            
        Returns:
            Réponse de l'API
        """
        endpoint = f"libraries/{library_id}/upload"
        
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'application/octet-stream')
            }
            data = metadata or {}
            
            return self._make_request(
                'post',
                endpoint,
                files=files,
                data=data
            )
    
    # Méthodes pour la lecture
    def get_progress(self, user_id: str, item_id: str) -> Dict:
        """Récupère la progression de lecture d'un utilisateur pour un livre."""
        return self._make_request('get', f'progress/{user_id}/{item_id}')
    
    def update_progress(self, user_id: str, item_id: str, progress: float, current_time: float) -> Dict:
        """Met à jour la progression de lecture."""
        endpoint = f'progress/{user_id}/{item_id}'
        data = {
            'progress': progress,
            'currentTime': current_time,
            'lastUpdate': int(datetime.now().timestamp() * 1000)
        }
        return self._make_request('post', endpoint, json=data)
    
    # Méthodes pour les métadonnées
    def get_metadata(self, item_id: str) -> Dict:
        """Récupère les métadonnées d'un livre."""
        return self._make_request('get', f'items/{item_id}/metadata')
    
    def update_metadata(self, item_id: str, metadata: Dict) -> Dict:
        """Met à jour les métadonnées d'un livre."""
        return self._make_request('post', f'items/{item_id}/metadata', json=metadata)
    
    # Méthodes pour les étiquettes
    def get_tags(self) -> List[str]:
        """Récupère toutes les étiquettes utilisées."""
        return self._make_request('get', 'tags')
    
    # Méthodes pour les séries
    def get_series(self) -> List[Dict]:
        """Récupère toutes les séries."""
        return self._make_request('get', 'series')
    
    def get_series_books(self, series_id: str) -> List[Dict]:
        """Récupère les livres d'une série."""
        return self._make_request('get', f'series/{series_id}/books')
    
    # Méthodes pour les tâches en arrière-plan
    def get_tasks(self) -> List[Dict]:
        """Récupère les tâches en cours."""
        return self._make_request('get', 'tasks')
    
    def get_task(self, task_name: str) -> Dict:
        """Récupère l'état d'une tâche spécifique."""
        return self._make_request('get', f'tasks/{task_name}')
    
    # Méthodes pour les paramètres du serveur
    def get_server_settings(self) -> Dict:
        """Récupère les paramètres du serveur (admin uniquement)."""
        return self._make_request('get', 'server/settings')
    
    def update_server_settings(self, settings: Dict) -> Dict:
        """Met à jour les paramètres du serveur (admin uniquement)."""
        return self._make_request('post', 'server/settings', json=settings)
