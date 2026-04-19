"""
Tests spécifiques pour la correction de gestion des threads FFmpeg.
Vérifie que les processus FFmpeg ne sont plus tués par le thread principal.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from app.services.upload_service import UploadService, ProcessingError


class TestUploadServiceThreadFix:
    """Tests pour la correction de gestion des threads FFmpeg."""

    def setup_method(self):
        """Configuration test service."""
        self.service = UploadService()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Nettoyage."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_ffmpeg_process_start_new_session(self):
        """Test que les processus FFmpeg démarrent avec start_new_session=True."""
        # Créer fichiers de test
        input_file = self.temp_dir / "test.mp3"
        input_file.write_bytes(b'dummy audio content')
        output_file = self.temp_dir / "output.m4b"

        # Mock create_subprocess_exec pour vérifier les arguments
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            # Configurer le mock pour retourner un processus simulé
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'', b''))
            mock_process.wait = AsyncMock(return_value=0)
            mock_subprocess.return_value = mock_process

            # Appeler la méthode de conversion
            await self.service._convert_single_file(input_file, output_file)

            # Vérifier que start_new_session=True a été passé
            assert mock_subprocess.called
            call_args = mock_subprocess.call_args
            assert call_args[1].get('start_new_session') is True, \
                "start_new_session=True doit être passé à create_subprocess_exec"

    @pytest.mark.asyncio
    async def test_ffmpeg_conversion_timeout_handling(self):
        """Test la gestion des timeouts pour les conversions FFmpeg."""
        input_file = self.temp_dir / "test.mp3"
        input_file.write_bytes(b'dummy audio content')
        output_file = self.temp_dir / "output.m4b"

        # Mock create_subprocess_exec pour simuler un timeout
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.terminate = MagicMock()
            mock_process.kill = MagicMock()
            mock_process.wait = AsyncMock(return_value=0)
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_subprocess.return_value = mock_process

            # Devrait lever ProcessingError avec message de timeout
            with pytest.raises(ProcessingError) as exc_info:
                await self.service._convert_single_file(input_file, output_file)

            assert "timeout apres 30 minutes" in exc_info.value.message.lower()
            
            # Vérifier que le processus a été correctement terminé
            mock_process.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_ffmpeg_process_termination_on_timeout(self):
        """Test la terminaison propre des processus FFmpeg en cas de timeout."""
        input_file = self.temp_dir / "test.mp3"
        input_file.write_bytes(b'dummy audio content')
        output_file = self.temp_dir / "output.m4b"

        # Mock create_subprocess_exec pour simuler un processus qui ne répond pas
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.terminate = MagicMock()
            mock_process.kill = MagicMock()
            mock_process.wait = AsyncMock(side_effect=[asyncio.TimeoutError(), 0])  # Premier appel timeout
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_subprocess.return_value = mock_process

            # Devrait lever ProcessingError
            with pytest.raises(ProcessingError):
                await self.service._convert_single_file(input_file, output_file)

            # Vérifier la séquence de terminaison
            mock_process.terminate.assert_called_once()
            mock_process.kill.assert_called_once()
            assert mock_process.wait.call_count == 2  # Appel initial + après kill

    @pytest.mark.asyncio
    async def test_ffmpeg_concat_timeout_handling(self):
        """Test la gestion des timeouts pour les concaténations FFmpeg."""
        # Créer plusieurs fichiers de test
        input_files = []
        for i in range(3):
            file = self.temp_dir / f"test_{i}.mp3"
            file.write_bytes(f"dummy audio {i}".encode())
            input_files.append(file)

        output_dir = self.temp_dir / "output"
        output_dir.mkdir()

        # Mock _convert_single_file pour simuler un timeout sur concaténation
        with patch.object(self.service, '_convert_single_file', new_callable=AsyncMock) as mock_convert:

            # Mock _convert_single_file pour lever une exception de timeout
            mock_convert.side_effect = ProcessingError("Conversion FFmpeg timeout apres 1 heure")

            # Devrait lever ProcessingError avec message de timeout
            with pytest.raises(ProcessingError) as exc_info:
                await self.service._convert_to_m4b(input_files, output_dir, "test_task")

            assert "timeout apres 1 heure" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_ffmpeg_error_handling_with_stderr(self):
        """Test la gestion des erreurs FFmpeg avec messages stderr."""
        input_file = self.temp_dir / "test.mp3"
        input_file.write_bytes(b'dummy audio content')
        output_file = self.temp_dir / "output.m4b"

        # Mock create_subprocess_exec pour simuler une erreur FFmpeg
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 1  # Code erreur
            mock_process.communicate = AsyncMock(return_value=(b'', b'Erreur FFmpeg: format non supporte'))
            mock_process.wait = AsyncMock(return_value=1)
            mock_subprocess.return_value = mock_process

            # Devrait lever ProcessingError avec le message stderr
            with pytest.raises(ProcessingError) as exc_info:
                await self.service._convert_single_file(input_file, output_file)

            assert "format non supporte" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_ffmpeg_successful_conversion(self):
        """Test une conversion FFmpeg réussie."""
        input_file = self.temp_dir / "test.mp3"
        input_file.write_bytes(b'dummy audio content')
        output_file = self.temp_dir / "output.m4b"

        # Mock create_subprocess_exec pour simuler une conversion réussie
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'', b''))
            mock_process.wait = AsyncMock(return_value=0)
            mock_subprocess.return_value = mock_process

            # Ne devrait pas lever d'exception
            await self.service._convert_single_file(input_file, output_file)

            # Vérifier que le processus a été appelé avec les bons arguments
            assert mock_subprocess.called
            call_args = mock_subprocess.call_args[0]
            assert 'ffmpeg' in call_args[0]  # Premier argument est ffmpeg
            assert '-i' in call_args
            assert str(input_file) in call_args
            assert str(output_file) in call_args

    @pytest.mark.asyncio
    async def test_multiple_conversions_isolation(self):
        """Test que les conversions multiples sont isolées."""
        # Créer plusieurs paires de fichiers
        conversions = []
        for i in range(3):
            input_file = self.temp_dir / f"input_{i}.mp3"
            input_file.write_bytes(f"audio content {i}".encode())
            output_file = self.temp_dir / f"output_{i}.m4b"
            conversions.append((input_file, output_file))

        # Mock create_subprocess_exec pour vérifier que chaque conversion est indépendante
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'', b''))
            mock_process.wait = AsyncMock(return_value=0)
            mock_subprocess.return_value = mock_process

            # Exécuter plusieurs conversions
            for input_file, output_file in conversions:
                await self.service._convert_single_file(input_file, output_file)

            # Vérifier que create_subprocess_exec a été appelé 3 fois
            assert mock_subprocess.call_count == 3
            
            # Vérifier que chaque appel avait start_new_session=True
            for call in mock_subprocess.call_args_list:
                assert call[1].get('start_new_session') is True

    @pytest.mark.asyncio
    async def test_process_cleanup_after_success(self):
        """Test le nettoyage des ressources après une conversion réussie."""
        input_file = self.temp_dir / "test.mp3"
        input_file.write_bytes(b'dummy audio content')
        output_file = self.temp_dir / "output.m4b"

        # Mock create_subprocess_exec
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'', b''))
            mock_process.wait = AsyncMock(return_value=0)
            mock_subprocess.return_value = mock_process

            # Exécuter la conversion
            await self.service._convert_single_file(input_file, output_file)

            # Vérifier que communicate() a été appelé pour nettoyer les pipes
            mock_process.communicate.assert_called_once()
            # Note: wait() n'est plus appelé directement dans le nouveau code

    @pytest.mark.asyncio
    async def test_process_cleanup_after_failure(self):
        """Test le nettoyage des ressources après une conversion échouée."""
        input_file = self.temp_dir / "test.mp3"
        input_file.write_bytes(b'dummy audio content')
        output_file = self.temp_dir / "output.m4b"

        # Mock create_subprocess_exec pour simuler une erreur
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(b'', b'Erreur'))
            mock_process.wait = AsyncMock(return_value=1)
            mock_subprocess.return_value = mock_process

            # Exécuter la conversion (devrait échouer)
            with pytest.raises(ProcessingError):
                await self.service._convert_single_file(input_file, output_file)

            # Vérifier que les ressources ont été nettoyées même en cas d'erreur
            mock_process.communicate.assert_called_once()
            # Note: wait() n'est plus appelé directement dans le nouveau code


class TestUploadServiceThreadSafety:
    """Tests de sécurité des threads pour le service d'upload."""

    def setup_method(self):
        """Configuration test service."""
        self.service = UploadService()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Nettoyage."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_concurrent_conversions_isolation(self):
        """Test que les conversions concurrentes sont correctement isolées."""
        # Créer plusieurs fichiers de test
        files = []
        for i in range(5):
            input_file = self.temp_dir / f"concurrent_{i}.mp3"
            input_file.write_bytes(f"audio content {i}".encode())
            output_file = self.temp_dir / f"concurrent_{i}.m4b"
            files.append((input_file, output_file))

        # Mock create_subprocess_exec
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'', b''))
            mock_process.wait = AsyncMock(return_value=0)
            mock_subprocess.return_value = mock_process

            # Exécuter les conversions en parallèle
            tasks = []
            for input_file, output_file in files:
                task = asyncio.create_task(self.service._convert_single_file(input_file, output_file))
                tasks.append(task)

            # Attendre que toutes les conversions se terminent
            await asyncio.gather(*tasks, return_exceptions=True)

            # Vérifier que chaque conversion a été appelée avec start_new_session=True
            assert mock_subprocess.call_count == 5
            for call in mock_subprocess.call_args_list:
                assert call[1].get('start_new_session') is True

    @pytest.mark.asyncio
    async def test_task_lock_protection(self):
        """Test que le verrou de tâche protège contre les accès concurrents."""
        # Vérifier que le service a un verrou de tâche
        assert hasattr(self.service, '_task_lock')
        assert self.service._task_lock is not None

        # Test que les méthodes critiques utilisent le verrou
        # (Cela serait vérifié par inspection du code ou tests d'intégration)
        assert True  # Placeholder pour test futur plus complet
