"""
Tests d'intégration pour la gestion des instances Audiobookshelf.
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService


@pytest.fixture
def db_session():
    """Fixture pour obtenir une session de base de données de test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def instance_service(db_session):
    """Fixture pour le service d'instances."""
    return AudiobookshelfInstanceService(db_session)


class TestAudiobookshelfInstanceService:
    """Tests pour AudiobookshelfInstanceService."""

    @patch('requests.post')
    def test_create_instance_success(self, mock_post, instance_service):
        """Test création réussie d'une instance."""
        # Mock de l'authentification réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user": {"token": "test-token-123", "username": "testuser"}
        }
        mock_post.return_value = mock_response

        # Mock du test de connexion
        with patch.object(instance_service, '_test_instance_connection') as mock_test:
            mock_test.return_value = ("v2.8.0", "active")

            # Création de l'instance
            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            assert instance is not None
            assert instance.name == "Test Server"
            assert instance.base_url == "https://audiobooks.test.com"
            assert instance.username == "testuser"
            assert instance.status == "active"
            assert instance.version == "v2.8.0"

    @patch('requests.post')
    def test_create_instance_auth_fail(self, mock_post, instance_service):
        """Test création d'instance avec échec d'authentification."""
        # Mock de l'authentification échouée
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        instance = instance_service.create_instance(
            name="Test Server",
            base_url="https://audiobooks.test.com",
            username="testuser",
            password="wrongpass"
        )

        assert instance is None

    def test_get_instance_not_found(self, instance_service):
        """Test récupération d'instance inexistante."""
        instance = instance_service.get_instance(999)
        assert instance is None

    def test_update_instance(self, instance_service):
        """Test mise à jour d'instance."""
        # D'abord créer une instance
        with patch('requests.post') as mock_post, \
             patch.object(instance_service, '_test_instance_connection') as mock_test:

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": {"token": "test-token", "username": "testuser"}}
            mock_post.return_value = mock_response
            mock_test.return_value = ("v2.8.0", "active")

            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            # Tester la mise à jour
            success = instance_service.update_instance(
                instance_id=instance.id,
                name="Updated Server",
                is_active=False
            )

            assert success
            updated = instance_service.get_instance(instance.id)
            assert updated.name == "Updated Server"
            assert not updated.is_active

    def test_rotate_token(self, instance_service):
        """Test rotation de token."""
        # D'abord créer une instance
        with patch('requests.post') as mock_post, \
             patch.object(instance_service, '_test_instance_connection') as mock_test, \
             patch('app.core.security.encrypt_token') as mock_encrypt, \
             patch('app.core.security.decrypt_token') as mock_decrypt:

            mock_encrypt.return_value = "encrypted-token"
            mock_decrypt.return_value = "decrypted-token"

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": {"token": "test-token", "username": "testuser"}}
            mock_post.return_value = mock_response
            mock_test.return_value = ("v2.8.0", "active")

            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            # Mock pour la rotation
            mock_post.return_value.json.return_value = {"user": {"token": "new-test-token"}}

            success = instance_service.rotate_token(instance.id, "newpassword")
            assert success

    @patch('requests.get')
    def test_test_connection_success(self, mock_get, instance_service):
        """Test test de connexion réussi."""
        # D'abord créer une instance
        with patch('requests.post') as mock_post, \
             patch.object(instance_service, '_test_instance_connection') as mock_test, \
             patch('app.core.security.encrypt_token') as mock_encrypt:

            mock_encrypt.return_value = "encrypted-token"

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": {"token": "test-token", "username": "testuser"}}
            mock_post.return_value = mock_response
            mock_test.return_value = ("v2.8.0", "active")

            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            # Mock du test de connexion
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"version": "v2.8.0"}

            result = instance_service.test_connection(instance.id)

            assert result["success"]
            assert result["version"] == "v2.8.0"
            assert result["status"] == "active"

    @patch('requests.get')
    def test_test_connection_failure(self, mock_get, instance_service):
        """Test test de connexion échoué."""
        # D'abord créer une instance
        with patch('requests.post') as mock_post, \
             patch.object(instance_service, '_test_instance_connection') as mock_test, \
             patch('app.core.security.encrypt_token') as mock_encrypt:

            mock_encrypt.return_value = "encrypted-token"

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": {"token": "test-token", "username": "testuser"}}
            mock_post.return_value = mock_response
            mock_test.return_value = ("v2.8.0", "active")

            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            # Mock d'échec de connexion
            mock_get.return_value.status_code = 500

            result = instance_service.test_connection(instance.id)

            assert not result["success"]
            assert result["status"] == "error"


class TestAudiobookshelfInstanceModel:
    """Tests pour le modèle AudiobookshelfInstance."""

    def test_should_retry_active_instance(self, instance_service):
        """Test logique de retry pour instance active."""
        # Création d'instance active sans erreurs
        with patch('requests.post') as mock_post, \
             patch.object(instance_service, '_test_instance_connection'), \
             patch('app.core.security.encrypt_token'):

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": {"token": "test-token", "username": "testuser"}}
            mock_post.return_value = mock_response

            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            instance.status = "active"
            assert instance.should_retry() is True

    def test_should_retry_error_instance_recent(self, instance_service):
        """Test logique de retry pour instance en erreur récente."""
        from datetime import datetime, timedelta

        # Création d'instance avec erreur récente
        with patch('requests.post') as mock_post, \
             patch.object(instance_service, '_test_instance_connection'), \
             patch('app.core.security.encrypt_token'):

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": {"token": "test-token", "username": "testuser"}}
            mock_post.return_value = mock_response

            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            instance.status = "error"
            instance.last_error_at = datetime.utcnow() - timedelta(minutes=2)  # 2 minutes ago
            assert instance.should_retry() is True

    def test_should_not_retry_error_instance_old(self, instance_service):
        """Test logique de non-retry pour instance en erreur ancienne."""
        from datetime import datetime, timedelta

        # Création d'instance avec erreur ancienne
        with patch('requests.post') as mock_post, \
             patch.object(instance_service, '_test_instance_connection'), \
             patch('app.core.security.encrypt_token'):

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"user": {"token": "test-token", "username": "testuser"}}
            mock_post.return_value = mock_response

            instance = instance_service.create_instance(
                name="Test Server",
                base_url="https://audiobooks.test.com",
                username="testuser",
                password="testpass"
            )

            instance.status = "critical_error"
            instance.last_error_at = datetime.utcnow() - timedelta(minutes=20)  # 20 minutes ago
            assert instance.should_retry() is False