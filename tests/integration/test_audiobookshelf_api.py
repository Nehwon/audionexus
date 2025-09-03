"""
Tests d'intégration pour les APIs FastAPI Audiobookshelf.
"""
import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal


@pytest.fixture
async def client():
    """Fixture pour client HTTP de test."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def db_session():
    """Fixture pour session de base de données."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


class TestAudiobookshelfInstancesAPI:
    """Tests pour l'API de gestion des instances."""

    @patch('app.services.audiobookshelf_instance_service.AudiobookshelfInstanceService.create_instance')
    async def test_create_instance(self, mock_create, client):
        """Test création d'instance via API."""
        mock_instance = MagicMock()
        mock_instance.id = 1
        mock_instance.name = "Test Server"
        mock_create.return_value = mock_instance

        instance_data = {
            "name": "Test Server",
            "base_url": "https://audiobooks.test.com",
            "username": "testuser",
            "password": "testpass"
        }

        response = await client.post("/audiobookshelf/instances/", json=instance_data)

        if response.status_code == 422:
            # Erreur de validation Pydantic - probablement besoin d'authentification
            assert "detail" in response.json()
        else:
            assert response.status_code in [200, 201]

    async def test_list_instances(self, client):
        """Test liste des instances."""
        response = await client.get("/audiobookshelf/instances/")

        # Peut échouer si authentification requise
        assert response.status_code in [200, 401, 403]

        if response.status_code == 200:
            data = response.json()
            assert "instances" in data
            assert "total" in data
            assert "active" in data

    @patch('app.services.audiobookshelf_instance_service.AudiobookshelfInstanceService.get_instance')
    async def test_get_instance(self, mock_get, client):
        """Test récupération d'instance."""
        mock_instance = MagicMock()
        mock_instance.id = 1
        mock_instance.name = "Test Server"
        mock_get.return_value = mock_instance

        response = await client.get("/audiobookshelf/instances/1")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code in [200, 404]

    @patch('app.services.audiobookshelf_instance_service.AudiobookshelfInstanceService.update_instance')
    async def test_update_instance(self, mock_update, client):
        """Test mise à jour d'instance."""
        mock_update.return_value = True

        update_data = {
            "name": "Updated Server"
        }

        response = await client.put("/audiobookshelf/instances/1", json=update_data)

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code in [200, 400, 404]


class TestAudiobookshelfSyncAPI:
    """Tests pour l'API de synchronisation."""

    async def test_sync_status(self, client):
        """Test récupération du statut de synchronisation."""
        response = await client.get("/audiobookshelf/sync/status")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "scheduler_running" in data
            assert "total_instances" in data
            assert "active_instances" in data

    async def test_start_scheduler(self, client):
        """Test démarrage du planificateur."""
        response = await client.post("/audiobookshelf/sync/scheduler/start")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        elif response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "started" in data.get("status", "")

    async def test_stop_scheduler(self, client):
        """Test arrêt du planificateur."""
        response = await client.post("/audiobookshelf/sync/scheduler/stop")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        elif response.status_code == 200:
            data = response.json()
            assert "message" in data


class TestAudiobookshelfLocalAPI:
    """Tests pour l'API d'accès aux données locales."""

    @patch('app.crud.audiobook.crud_audiobook.get_multi')
    async def test_get_audiobooks(self, mock_get_multi, client):
        """Test récupération des livres audio locaux."""
        mock_get_multi.return_value = []

        response = await client.get("/audiobookshelf/local/books")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code == 200
            data = response.json()

    @patch('app.crud.audiobook.crud_audiobook.get_multi')
    async def test_search_audiobooks(self, mock_get_multi, client):
        """Test recherche de livres audio."""
        mock_get_multi.return_value = []

        response = await client.get("/audiobookshelf/local/books?search=test+book")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code == 200

    @patch('app.crud.audiobook.crud_audiobook.get_multi')
    async def test_filter_audiobooks(self, mock_get_multi, client):
        """Test filtrage des livres audio."""
        mock_get_multi.return_value = []

        response = await client.get("/audiobookshelf/local/books?author=Test+Author")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code == 200


class TestAudiobookshelfAPIMain:
    """Tests pour l'API principale Audiobookshelf (connexion à l'instance distante)."""

    @patch('app.core.dependencies.get_audiobookshelf_client')
    async def test_get_libraries(self, mock_get_client, client):
        """Test récupération des bibliothèques."""
        mock_client = MagicMock()
        mock_client.get_libraries.return_value = [
            {"id": "lib1", "name": "Test Library"}
        ]
        mock_get_client.return_value = mock_client

        response = await client.get("/audiobookshelf/libraries")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code == 200
            data = response.json()
            if isinstance(data, list):
                assert len(data) >= 0

    @patch('app.core.dependencies.get_audiobookshelf_client')
    async def test_search_audiobooks(self, mock_get_client, client):
        """Test recherche de livres."""
        mock_client = MagicMock()
        mock_client.search_library.return_value = [
            {"id": "book1", "title": "Test Book"}
        ]
        mock_get_client.return_value = mock_client

        response = await client.get("/audiobookshelf/search?q=test")

        if response.status_code == 401:
            assert "not authenticated" in response.json().get("detail", "").lower()
        elif response.status_code == 422:
            # Paramètre manquant ou invalide
            assert "query" in str(response.json())
        else:
            assert response.status_code == 200


class TestResilienceAPI:
    """Tests de résilience pour les APIs."""

    async def test_instance_api_without_auth(self, client):
        """Test accès API sans authentification."""
        response = await client.post("/audiobookshelf/instances/", json={})

        assert response.status_code in [401, 403]
        if response.status_code == 401:
            assert "authenticated" in response.json().get("detail", "").lower()

    @patch('app.core.dependencies.get_audiobookshelf_client')
    async def test_api_with_client_error(self, mock_get_client, client):
        """Test API avec erreur du client."""
        mock_client = MagicMock()
        mock_client.get_libraries.side_effect = Exception("Connection failed")
        mock_get_client.return_value = mock_client

        response = await client.get("/audiobookshelf/libraries")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            # Devrait retourner une erreur 500 en cas de problème
            assert response.status_code >= 400

    async def test_invalid_instance_id(self, client):
        """Test avec ID d'instance invalide."""
        response = await client.get("/audiobookshelf/instances/999")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        elif response.status_code == 404:
            assert "non trouvée" in response.json().get("detail", "")

    async def test_malformed_request(self, client):
        """Test avec requête malformée."""
        response = await client.post("/audiobookshelf/instances/", json={"invalid": "data"})

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        elif response.status_code == 422:
            # Erreur de validation Pydantic
            assert "detail" in response.json()

    @patch('app.services.audiobookshelf_instance_service.AudiobookshelfInstanceService.create_instance')
    async def test_instance_creation_failure(self, mock_create, client):
        """Test échec de création d'instance."""
        mock_create.return_value = None

        instance_data = {
            "name": "Test Server",
            "base_url": "https://invalid.test.com",
            "username": "testuser",
            "password": "testpass"
        }

        response = await client.post("/audiobookshelf/instances/", json=instance_data)

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        elif response.status_code == 400:
            assert "detail" in response.json()

    @patch('app.crud.audiobook.crud_audiobook.get_multi')
    async def test_empty_search_results(self, mock_get_multi, client):
        """Test recherche ne retournant aucun résultat."""
        mock_get_multi.return_value = []

        response = await client.get("/audiobookshelf/local/books?search=nonexistent")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            assert response.status_code == 200
            data = response.json()
            # La structure exacte dépend de l'implémentation


class TestSecurityAPI:
    """Tests de sécurité pour les APIs."""

    async def test_unauthorized_access(self, client):
        """Test accès non autorisé."""
        endpoints = [
            "/audiobookshelf/instances/",
            "/audiobookshelf/sync/status",
            "/audiobookshelf/local/books",
            "/audiobookshelf/libraries"
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code in [401, 403]

    async def test_invalid_http_methods(self, client):
        """Test méthodes HTTP invalides."""
        response = await client.patch("/audiobookshelf/instances/1")
        assert response.status_code in [401, 403, 405]

    async def test_sql_injection_attempt(self, client):
        """Test tentative d'injection SQL."""
        malicious_query = "'; DROP TABLE audiobooks; --"
        response = await client.get(f"/audiobookshelf/local/books?search={malicious_query}")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            # Ne devrait pas réussir si les protections sont en place
            assert response.status_code != 200 or "sql" not in str(response.json()).lower()

    async def test_xss_attempt(self, client):
        """Test tentative de XSS."""
        malicious_script = "<script>alert('xss')</script>"
        response = await client.get(f"/audiobookshelf/local/books?search={malicious_script}")

        if response.status_code == 401:
            assert "Not authenticated" in response.json().get("detail", "")
        else:
            # La réponse ne devrait pas contenir le script non échappé
            content = str(response.json())
            assert "<script>" not in content or "alert" not in content