"""
Tests d'intégration pour la synchronisation Audiobookshelf.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.audiobookshelf_sync import AudiobookshelfSyncService
from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService
from app.crud.audiobookshelf_instance import crud_audiobookshelf_instance


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
def test_instance(db_session):
    """Fixture pour créer une instance de test."""
    instance_service = AudiobookshelfInstanceService(db_session)

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

        return instance


class TestAudiobookshelfSyncService:
    """Tests pour AudiobookshelfSyncService."""

    def test_init_without_instance(self, db_session):
        """Test d'initialisation du service sans instance spécifiée."""
        sync_service = AudiobookshelfSyncService(db_session=db_session)
        assert sync_service.instance_id is None
        assert sync_service.audioshelf_client is None

    def test_init_with_instance(self, db_session, test_instance):
        """Test d'initialisation du service avec une instance existante."""
        with patch.object(AudiobookshelfSyncService, '_init_client') as mock_init:
            mock_init.return_value = True

            sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)
            assert sync_service.instance_id == test_instance.id
            assert sync_service.audioshelf_client is None  # Car mocké

    def test_set_instance_success(self, db_session, test_instance):
        """Test définition d'instance réussie."""
        sync_service = AudiobookshelfSyncService(db_session=db_session)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client:

            mock_decrypt.return_value = "decrypted-token"
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            success = sync_service.set_instance(test_instance.id)

            assert success
            assert sync_service.instance_id == test_instance.id
            assert sync_service.audioshelf_client == mock_client_instance

    def test_set_instance_not_found(self, db_session):
        """Test définition d'instance inexistante."""
        sync_service = AudiobookshelfSyncService(db_session=db_session)

        success = sync_service.set_instance(999)
        assert not success
        assert sync_service.audioshelf_client is None

    def test_sync_all_without_client(self, db_session):
        """Test synchronisation sans client initialisé."""
        sync_service = AudiobookshelfSyncService(db_session=db_session)

        result = sync_service.sync_all()

        assert result['errors'] == 1
        assert result['libraries_synced'] == 0
        assert result['audiobooks_synced'] == 0
        assert result['progress_updated'] == 0

    def test_sync_all_with_client(self, db_session, test_instance):
        """Test synchronisation complète avec client mocké."""
        sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client_class:

            mock_decrypt.return_value = "decrypted-token"

            # Mock du client
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock des appels API
            mock_client.get_libraries.return_value = [
                {"id": "lib1", "name": "Test Library"}
            ]
            mock_client.search_audiobooks.return_value = []

            # Initialiser le client
            sync_service.set_instance(test_instance.id)

            # Exécuter la synchronisation
            result = sync_service.sync_all()

            # Le résultat pourra varier selon l'implémentation
            assert isinstance(result, dict)
            assert 'errors' in result
            assert 'libraries_synced' in result
            assert 'audiobooks_synced' in result
            assert 'progress_updated' in result

    def test_sync_libraries(self, db_session, test_instance):
        """Test synchronisation des bibliothèques."""
        sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client_class:

            mock_decrypt.return_value = "decrypted-token"

            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get_libraries.return_value = [
                {"id": "lib1", "name": "Test Library 1"},
                {"id": "lib2", "name": "Test Library 2"}
            ]

            sync_service.set_instance(test_instance.id)
            libraries_count = sync_service.sync_libraries()

            assert libraries_count == 2
            mock_client.get_libraries.assert_called_once()

    def test_sync_audiobooks(self, db_session, test_instance):
        """Test synchronisation des livres audio."""
        sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client_class, \
             patch.object(sync_service, '_process_audiobook_batch') as mock_process:

            mock_decrypt.return_value = "decrypted-token"

            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock de la structure de bibliothèque et résultats de recherche
            mock_client.get_libraries.return_value = [
                {"id": "lib1", "name": "Test Library"}
            ]
            mock_client.search_library.return_value = [
                {"id": "book1", "title": "Test Book", "metadata": {"title": "Test Book"}},
                {"id": "book2", "title": "Another Book", "metadata": {"title": "Another Book"}}
            ]

            mock_process.return_value = {'processed': 2, 'updated': 0, 'created': 2, 'errors': 0}

            sync_service.set_instance(test_instance.id)
            result = sync_service.sync_audiobooks()

            assert result == 2  # 2 livres traités
            mock_client.get_libraries.assert_called_once()

    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_scheduler_sync(self, mock_sleep):
        """Test du planificateur de synchronisation."""
        from app.services.audiobookshelf_scheduler import AudiobookshelfSchedulerService

        scheduler = AudiobookshelfSchedulerService()

        # Mock pour revenir après quelques secondes
        mock_sleep.side_effect = lambda x: (_ for _ in ()).throw(KeyboardInterrupt()) if x == 3600 else None

        try:
            await scheduler.start_scheduler()
        except KeyboardInterrupt:
            pass  # Expected interruption

        # Vérifier que le scheduler était actif
        assert not scheduler._running

    def test_get_decrypted_token_success(self, db_session, test_instance):
        """Test récupération de token déchiffré avec succès."""
        with patch('app.core.security.decrypt_token') as mock_decrypt:
            mock_decrypt.return_value = "decrypted-token-123"

            sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

            token = sync_service.instance_service.get_decrypted_token(test_instance.id)

            assert token == "decrypted-token-123"
            mock_decrypt.assert_called_once_with(test_instance.api_token)

    def test_get_decrypted_token_failure(self, db_session):
        """Test récupération de token échoué."""
        sync_service = AudiobookshelfSyncService(db_session=db_session)

        token = sync_service.instance_service.get_decrypted_token(999)

        assert token is None


class TestSyncResilience:
    """Tests de résilience pour la synchronisation."""

    def test_sync_with_network_timeout(self, db_session, test_instance):
        """Test synchronisation avec timeout réseau."""
        sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client_class:

            mock_decrypt.return_value = "decrypted-token"

            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Simuler un timeout réseau
            mock_client.get_libraries.side_effect = TimeoutError("Connection timeout")

            sync_service.set_instance(test_instance.id)
            result = sync_service.sync_all()

            # Devrait avoir enregistré une erreur
            assert result['errors'] > 0

    def test_sync_with_invalid_response(self, db_session, test_instance):
        """Test synchronisation avec réponse invalide."""
        sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client_class:

            mock_decrypt.return_value = "decrypted-token"

            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Réponse JSON invalide
            mock_client.get_libraries.side_effect = ValueError("Invalid JSON")

            sync_service.set_instance(test_instance.id)
            result = sync_service.sync_all()

            assert result['errors'] > 0

    def test_partial_sync_failure(self, db_session, test_instance):
        """Test synchronisation partielle avec certaines échecs."""
        sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client_class:

            mock_decrypt.return_value = "decrypted-token"

            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Bibliothèques OK
            mock_client.get_libraries.return_value = [
                {"id": "lib1", "name": "Library 1"},
                {"id": "lib2", "name": "Library 2"}
            ]

            # Recherche échoue pour la première bibliothèque
            def search_side_effect(library_id, query):
                if library_id == "lib1":
                    raise ConnectionError("Network error")
                return [{"id": "book1", "title": "Test Book"}]

            mock_client.search_library.side_effect = search_side_effect

            sync_service.set_instance(test_instance.id)
            result = sync_service.sync_all()

            # Devrait avoir synchronisé 1 bibliothèque sur 2
            assert result['libraries_synced'] == 2  # Toujours compté même si une partie échoue
            assert result['errors'] > 0  # Erreur dans la synchronisation des livres

    def test_initial_sync_resilience(self, db_session, test_instance):
        """Test synchronisation initiale avec récupération d'erreurs."""
        sync_service = AudiobookshelfSyncService(db_session=db_session, instance_id=test_instance.id)

        with patch('app.core.security.decrypt_token') as mock_decrypt, \
             patch('app.core.api.audiobookshelf.AudiobookshelfClient') as mock_client_class, \
             patch.object(sync_service, '_process_audiobook_batch') as mock_process:

            mock_decrypt.return_value = "decrypted-token"

            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Bibliothèques avec des erreurs partielles
            mock_client.get_libraries.return_value = [{"id": "lib1", "name": "Test Library"}]
            mock_client.search_library.return_value = [
                {"id": "book1", "metadata": {"title": "Book 1"}},
                {"id": "book2", "metadata": {"title": "Book 2"}}
            ]

            # Le traitement échoue pour le premier livre
            mock_process.return_value = {'processed': 1, 'updated': 1, 'created': 0, 'errors': 1}

            sync_service.set_instance(test_instance.id)
            result = sync_service.initial_sync(batch_size=50)

            # Devrait continuer malgré l'erreur sur un livre
            assert result['audiobooks_synced'] == 1
            assert result['errors'] == 1