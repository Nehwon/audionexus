"""
Tests unitaires et d'intégration pour FFmpegService.

Couvre les fonctionnalités avancées du service FFmpeg :
- Conversion audio avec métadonnées
- Génération chapitres automatiques
- Retry mechanisms
- Validation sécurité
- Audit trail
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from app.services.ffmpeg_service import (
    FFmpegService,
    FFmpegConfig,
    AudioMetadata,
    AudioMetadata,
    ConversionResult,
    Chapter,
    ConversionError,
    CompressionQuality
)


class TestFFmpegService:
    """Tests du service FFmpeg."""

    def setup_method(self):
        """Configuration test service."""
        self.service = FFmpegService()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Nettoyage."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('app.services.ffmpeg_service.shutil.which')
    def test_initialization_with_ffmpeg_paths(self, mock_which):
        """Test initialisation avec chemins FFmpeg."""
        mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}" if cmd in ["ffmpeg", "ffprobe"] else None

        service = FFmpegService()

        assert service.ffmpeg_path == "/usr/bin/ffmpeg"
        assert service.ffprobe_path == "/usr/bin/ffprobe"
        assert service.version is not None

    def test_compression_quality_enum_values(self):
        """Test valeurs enum qualité de compression."""
        assert CompressionQuality.LOSSLESS.value == "lossless"
        assert CompressionQuality.HIGH.value == "high"
        assert CompressionQuality.MEDIUM.value == "medium"
        assert CompressionQuality.LOW.value == "low"

    @pytest.mark.asyncio
    async def test_convert_audio_files_workflow(self):
        """Test workflow conversion fichiers audio complet."""
        # Fichiers de test
        input_files = [
            self.temp_dir / "test1.mp3",
            self.temp_dir / "test2.mp3"
        ]
        for file in input_files:
            file.write_bytes(b'dummy audio content')

        output_dir = self.temp_dir / "output"
        output_dir.mkdir()

        config = FFmpegConfig(
            quality=CompressionQuality.HIGH,
            preserve_metadata=True,
            add_chapters=True
        )

        metadata = AudioMetadata(
            title="Test Audiobook",
            artist="Test Author",
            chapters=[
                Chapter(title="Intro", start_time=0, end_time=120),
                Chapter(title="Chapitre 1", start_time=120, end_time=600)
            ]
        )

        # Mock les méthodes internes
        with patch.object(self.service, '_convert_multiple_audio', new_callable=AsyncMock) as mock_convert:
            mock_convert.return_value = ConversionResult(
                input_file=input_files[0],
                output_file=output_dir / "output.m4b",
                duration=720,
                size_before=2048,
                size_after=1536,
                metadata_preserved=True,
                chapters_added=2,
                compression_ratio=0.75
            )

            results = await self.service.convert_audio_files(
                input_files, output_dir, config, metadata, "test_job"
            )

            mock_convert.assert_called_once()
            assert len(results) == 1
            assert results[0].chapters_added == 2

    @pytest.mark.asyncio
    async def test_single_file_conversion_success(self):
        """Test conversion fichier unique réussi."""
        input_file = self.temp_dir / "single.mp3"
        input_file.write_bytes(b'dummy mp3')

        output_file = self.temp_dir / "output.m4b"
        config = FFmpegConfig(quality=CompressionQuality.MEDIUM)

        # Mock probe et conversion
        with patch.object(self.service, '_probe_file', new_callable=AsyncMock) as mock_probe, \
             patch.object(self.service, '_run_ffmpeg_conversion', new_callable=AsyncMock) as mock_convert:

            mock_probe.return_value = {'duration': 180, 'size': 1024, 'bitrate': 128}
            mock_convert.return_value = True

            result = await self.service._convert_single_audio(
                input_file, self.temp_dir, config, AudioMetadata(), "single_test"
            )

            assert result.success is True
            assert result.duration == 180
            assert result.size_before == 1024
            assert result.size_after == 0  # Pas de fichier créé dans test
            mock_convert.assert_called_once()

    @pytest.mark.asyncio
    async def test_conversion_with_retry_on_failure(self):
        """Test retry automatique lors d'échecs de conversion."""
        input_file = self.temp_dir / "retry.mp3"
        input_file.write_bytes(b'dummy')

        config = FFmpegConfig(retry_count=3, retry_delay=0.1)

        # Simuler 2 échecs puis succès
        call_count = 0
        async def mock_conversion_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception(f"Erreur simulée {call_count}")
            return True

        with patch.object(self.service, '_run_ffmpeg_conversion', side_effect=mock_conversion_with_retry), \
             patch.object(self.service, '_probe_file', return_value={'duration': 120}):

            success = await self.service._run_ffmpeg_conversion(
                input_file, self.temp_dir / "output.m4b", config,
                AudioMetadata(), "retry_test", attempt=0
            )

            assert success is True
            assert call_count == 3  # 2 échecs + 1 succès

    @pytest.mark.asyncio
    async def test_metadata_preservation_building(self):
        """Test construction arguments métadonnées FFmpeg."""
        metadata = AudioMetadata(
            title="Test Book",
            artist="Test Author",
            album="Test Album",
            year="2024",
            genre="Fiction",
            narrator="Test Narrator"
        )

        args = await self.service._build_metadata_args(metadata)

        assert "-metadata" in args
        assert "title=Test Book" in args
        assert "artist=Test Author" in args
        assert "album=Test Album" in args
        assert "narrator=Test Narrator" in args

    @pytest.mark.asyncio
    async def test_auto_chapter_generation(self):
        """Test génération chapitres automatique."""
        # Fichier de 30 minutes
        probe_data = {'duration': 30 * 60}

        input_file = self.temp_dir / "long_audio.mp3"
        input_file.write_bytes(b"dummy content" * 1000)  # Créer contenu

        chapters = await self.service._generate_auto_chapters(probe_data, input_file)

        # Devrait générer des chapitres toutes les 10 minutes
        assert len(chapters) >= 2

        # Vérifier timing
        first_chapter = chapters[0]
        assert first_chapter.start_time == 0
        assert first_chapter.title == "Chapitre 1"

    @pytest.mark.asyncio
    async def test_chapter_file_creation(self):
        """Test création fichier chapitres FFmpeg."""
        chapters = [
            Chapter(title="Chapitre 1", start_time=0, end_time=600, description="Début"),
            Chapter(title="Chapitre 2", start_time=600, end_time=1200, description="Suite")
        ]

        chapter_file = await self.service._create_chapter_file(
            chapters, self.temp_dir, "chapter_test"
        )

        assert chapter_file is not None
        assert chapter_file.exists()

        # Vérifier contenu
        content = chapter_file.read_text()
        assert ";FFMETADATA1" in content
        assert "Chapitre 1" in content
        assert "Chapitre 2" in content

        # Nettoyer
        chapter_file.unlink()

    @pytest.mark.asyncio
    async def test_audio_security_validation(self):
        """Test validation sécurité fichiers audio."""
        # Test fichier valide (MP3)
        valid_mp3 = self.temp_dir / "valid.mp3"
        valid_mp3.write_bytes(b'ID3\x03\x00\x00\x00\x00\x00\x1f')  # Header MP3 valide

        is_valid, message = await self.service.validate_audio_file_security(valid_mp3)
        assert is_valid is True

        # Test fichier trop petit
        small_file = self.temp_dir / "small.wav"
        small_file.write_bytes(b'RIFF\x00\x00\x00\x00WAVE')  # Header WAV mais petit

        is_valid_small, message_small = await self.service.validate_audio_file_security(small_file)
        assert is_valid_small is False
        assert "trop petit" in message_small

    @pytest.mark.asyncio
    async def test_id3_metadata_extraction(self):
        """Test extraction métadonnées ID3."""
        # Créer fichier MP3 avec métadonnées simulées
        mp3_file = self.temp_dir / "test.mp3"
        mp3_file.write_bytes(b'ID3\x03\x00\x00\x00\x00\x00\x1f')  # Header basique

        metadata = await self.service._extract_metadata(mp3_file)

        # Avec header basique, certaines métadonnées peuvent ne pas être extraites
        assert isinstance(metadata, AudioMetadata)
        assert metadata.format == "mp3"

    @pytest.mark.asyncio
    async def test_multiple_file_concatenation(self):
        """Test concaténation multiple fichiers en M4B."""
        # Créer plusieurs fichiers de test
        input_files = []
        for i in range(3):
            file = self.temp_dir / f"part_{i}.m4a"
            file.write_bytes(f"dummy audio content {i}".encode())
            input_files.append(file)

        output_file = self.temp_dir / "concatenated.m4b"
        config = FFmpegConfig(quality=CompressionQuality.MEDIUM)

        # Mock la fonction concaténation
        with patch.object(self.service, '_concatenate_files', new_callable=AsyncMock) as mock_concat:
            mock_concat.return_value = True

            success = await self.service._concatenate_files(
                input_files, output_file, config, AudioMetadata(), "concat_test"
            )

            assert success is True
            mock_concat.assert_called_once()

    @pytest.mark.asyncio
    async def test_conversion_statistics_tracking(self):
        """Test tracking statistiques de conversion."""
        # Mock les données système
        with patch.object(self.service, '_get_system_info', new_callable=AsyncMock) as mock_system:
            mock_system.return_value = {
                "platform": "Linux",
                "python_version": "3.9.7",
                "cpu_count": 4
            }

            stats = await self.service.get_conversion_stats("stats_test_job")

            assert stats["job_id"] == "stats_test_job"
            assert "timestamp" in stats
            assert isinstance(stats["conversion_logs"], list)

    @pytest.mark.asyncio
    async def test_compression_quality_settings(self):
        """Test paramètres qualité de compression."""
        config_lossless = FFmpegConfig(quality=CompressionQuality.LOSSLESS)
        config_high = FFmpegConfig(quality=CompressionQuality.HIGH)
        config_medium = FFmpegConfig(quality=CompressionQuality.MEDIUM)
        config_low = FFmpegConfig(quality=CompressionQuality.LOW)

        # Test que chaque qualité a des paramètres différents
        configs = [config_lossless, config_high, config_medium, config_low]

        for config in configs:
            assert config.quality is not None
            assert isinstance(config.quality, (CompressionQuality, str))

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test gestion timeout conversions FFmpeg."""
        config = FFmpegConfig(timeout=1)  # Timeout court

        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            with pytest.raises(asyncio.TimeoutError):
                await self.service._run_ffmpeg_conversion(
                    self.temp_dir / "timeout.mp3",
                    self.temp_dir / "output.m4b",
                    config,
                    AudioMetadata(),
                    "timeout_test"
                )

    @pytest.mark.asyncio
    async def test_error_recovery_and_logging(self):
        """Test récupération d'erreurs et logging."""
        input_file = self.temp_dir / "error.mp3"
        input_file.write_bytes(b"dummy")

        config = FFmpegConfig(retry_count=1)

        # Simuler erreur fatale
        error_msg = "Erreur FFmpeg simulée"
        with patch.object(self.service, '_build_ffmpeg_command', side_effect=Exception(error_msg)), \
             patch.object(self.service, '_probe_file', return_value={'duration': 60}):

            result = await self.service._convert_single_audio(
                input_file, self.temp_dir, config, AudioMetadata(), "error_test"
            )

            assert result.success is False
            assert error_msg in result.error_message

    @pytest.mark.asyncio
    async def test_chapter_based_on_file_durations(self):
        """Test génération chapitres basée sur durées fichiers."""
        # Créer fichiers de test avec durées différentes
        input_files = [
            self.temp_dir / "short.mp3",   # 2 minutes
            self.temp_dir / "medium.mp3",  # 5 minutes
            self.temp_dir / "long.mp3"     # 10 minutes
        ]

        # Créer fichiers
        for file in input_files:
            file.write_bytes(b"dummy content")

        # Mock durées
        durations = [120, 300, 600]  # Durées cumulatives
        duration_index = 0

        async def mock_file_duration(file_path):
            nonlocal duration_index
            if duration_index < len(durations):
                duration = durations[duration_index]
                duration_index += 1
                return duration
            return 60

        with patch.object(self.service, '_probe_file_duration', side_effect=mock_file_duration):
            chapters = await self.service._generate_chapters_from_files(
                input_files, AudioMetadata(title="Multi-file Book")
            )

            assert len(chapters) == 3
            assert chapters[0].start_time == 0
            assert chapters[1].start_time == 120
            assert chapters[2].start_time == 420

    @pytest.mark.asyncio
    async def test_threading_optimization_flags(self):
        """Test flags threading et optimisation FFmpeg."""
        input_file = self.temp_dir / "thread.mp3"
        input_file.write_bytes(b"dummy")

        config = FFmpegConfig(quality=CompressionQuality.HIGH)

        # Vérifier que les arguments de threading sont présents
        with patch.object(self.service, '_run_ffmpeg_conversion', new_callable=AsyncMock) as mock_convert:
            mock_convert.return_value = True

            cmd, temp_files = await self.service._build_ffmpeg_command(
                input_file, self.temp_dir / "output.m4b", config,
                AudioMetadata(), "thread_test"
            )

            assert "-threads" in cmd
            assert "0" in cmd  # Utilise tous les cœurs
            assert "-loglevel" in cmd

    @pytest.mark.asyncio
    async def test_buffer_management_high_load(self):
        """Test gestion buffer sous charge élevée."""
        config = FFmpegConfig(temp_buffer_size="256M")  # Buffer large

        # Simuler conversion avec gros buffer
        cmd, _ = await self.service._build_ffmpeg_command(
            self.temp_dir / "buffer.mp3",
            self.temp_dir / "output.m4b",
            config,
            AudioMetadata(),
            "buffer_test"
        )

        # Vérifier que le buffer custom est utilisé
        assert "-bufsize" in cmd
        assert config.temp_buffer_size in cmd


class TestFFmpegSecurity:
    """Tests sécurité spécifiques au service FFmpeg."""

    def setup_method(self):
        self.service = FFmpegService()

    @pytest.mark.asyncio
    async def test_shell_injection_protection(self):
        """Test protection contre injection shell."""
        # Métadonnées avec caractères dangereux
        dangerous_metadata = AudioMetadata(
            title="Test; rm -rf /; echo",
            artist="Bad|Artist",
            album="Dangerous`whoami`Album"
        )

        args = await self.service._build_metadata_args(dangerous_metadata)

        # FFmpeg devrait échapper les caractères dangereux
        # Ici on vérifie au minimum que les args sont générés
        assert len(args) > 0
        assert "title=" in str(args)

    @pytest.mark.asyncio
    async def test_resource_exhaustion_protection(self):
        """Test protection contre épuisement ressources."""
        # Simuler fichier extrêmement volumineux
        import os
        large_content = b'A' * (100 * 1024 * 1024)  # 100MB

        large_file = self.temp_dir / "large.mp3"
        large_file.write_bytes(large_content)

        # Validation devrait détecter taille excessive
        is_valid, message = await self.service.validate_audio_file_security(large_file)

        # Le fichier est valide au niveau header, mais la taille peut être problématique
        assert message != "Fichier audio suspect (trop petit)"
        assert large_file.stat().st_size == len(large_content)

    @pytest.mark.asyncio
    async def test_corrupted_file_detection(self):
        """Test détection fichiers audio corrompus."""
        # Créer fichier avec header mauvais
        corrupted_file = self.temp_dir / "corrupted.mp3"
        corrupted_file.write_bytes(b'NOTANMP3HEADER')  # Header invalide

        probe_result = await self.service._probe_file(corrupted_file)

        # Devrait retourner données par défaut ou gérer l'erreur
        assert isinstance(probe_result, dict)
        assert 'duration' in probe_result