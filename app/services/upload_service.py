"""
Service de traitement des uploads d'audiobooks.
Gère la validation, extraction, conversion et traitement des métadonnées.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import patoolib
import rarfile
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TALB, TCON, TDRC, TIT2, TPE1, TRCK
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class UploadTask:
    """Représente une tâche d'upload en cours ou terminée."""

    task_id: str
    user_id: int
    status: str  # 'processing', 'completed', 'failed', 'cancelled'
    filename: str
    file_size: int
    upload_path: Optional[str] = None
    progress: float = 0.0
    current_step: str = ""
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class AudioMetadata:
    """Métadonnées extraites d'un fichier audio."""

    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[str] = None
    track_number: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    format: Optional[str] = None
    chapters: Optional[List[Dict[str, Any]]] = None


class UploadValidationError(ValidationError):
    """Erreur spécifique à la validation d'upload."""

    pass


class ExtractionError(ValidationError):
    """Erreur lors de l'extraction d'archive."""

    pass


class ProcessingError(ValidationError):
    """Erreur générale lors du traitement."""

    pass


class UploadService:
    """Service principal pour la gestion des uploads d'audiobooks."""

    # Formats audio supportés
    SUPPORTED_AUDIO_FORMATS = {
        ".mp3",
        ".m4a",
        ".m4b",
        ".aac",
        ".flac",
        ".ogg",
        ".wma",
        ".wav",
    }

    # Formats d'archive supportés
    SUPPORTED_ARCHIVE_FORMATS = {".zip", ".rar", ".7z", ".tar.gz", ".tar.bz2"}

    def __init__(self):
        """Initialise le service d'upload."""
        self.temp_dir = (
            Path(settings.UPLOAD_FOLDER or tempfile.gettempdir()) / "audiobooks_uploads"
        )
        self.temp_dir.mkdir(exist_ok=True)

        # Cache des tâches en mémoire (pour développement)
        self._tasks_cache: Dict[str, UploadTask] = {}
        self._task_lock = asyncio.Lock()

        # Configuration FFmpeg
        self.ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"
        self.ffprobe_path = shutil.which("ffprobe") or "ffprobe"

    async def validate_upload(self, file: UploadFile) -> None:
        """
        Valide le fichier uploadé.

        Args:
            file: Fichier uploadé

        Raises:
            UploadValidationError: Si le fichier n'est pas valide
        """
        # Vérification de la taille (max 500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        if hasattr(file, "size") and file.size > max_size:
            raise UploadValidationError(
                f"Fichier trop volumineux (max: 500MB, actuel: {file.size / (1024*1024):.1f}MB)"
            )

        # Vérification du type de fichier
        filename = file.filename.lower() if file.filename else ""
        if not filename:
            raise UploadValidationError("Nom de fichier manquant")

        # Vérification de l'extension
        file_ext = Path(filename).suffix
        if file_ext not in self.SUPPORTED_ARCHIVE_FORMATS:
            raise UploadValidationError(
                f"Format non supporté. Formats acceptés: {', '.join(self.SUPPORTED_ARCHIVE_FORMATS)}"
            )

        # Vérification du type MIME
        content_type = getattr(file, "content_type", "")
        allowed_mimes = [
            "application/zip",
            "application/x-rar-compressed",
            "application/x-7z-compressed",
        ]
        if content_type and content_type not in allowed_mimes:
            # Log mais ne pas bloquer - certains clients envoient des types génériques
            logger.warning(f"Type MIME inattendu: {content_type}")

        logger.info(f"Fichier validé: {filename} ({getattr(file, 'size', 0)} bytes)")

    async def save_temporary_file(self, file: UploadFile, task_id: str) -> Path:
        """
        Sauvegarde temporairement le fichier uploadé.

        Args:
            file: Fichier uploadé
            task_id: ID de la tâche

        Returns:
            Chemin vers le fichier temporaire
        """
        temp_path = self.temp_dir / f"{task_id}_{file.filename}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            logger.info(f"Fichier temporaire sauvegardé: {temp_path}")
            return temp_path

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde temporaire: {e}")
            raise ProcessingError(f"Erreur de sauvegarde du fichier: {str(e)}")

    async def process_audiobook_archive(
        self, task_id: str, upload_path: Path, user_id: int, db: Session
    ) -> None:
        """
        Traite automatiquement une archive d'audiobook.

        Args:
            task_id: Identifiant de la tâche
            upload_path: Chemin vers l'archive
            user_id: ID de l'utilisateur
            db: Session de base de données
        """
        task = UploadTask(
            task_id=task_id,
            user_id=user_id,
            status="processing",
            filename=upload_path.name,
            file_size=upload_path.stat().st_size,
            upload_path=str(upload_path),
            current_step="extraction",
        )

        async with self._task_lock:
            self._tasks_cache[task_id] = task

        try:
            # Étape 1: Extraction de l'archive
            logger.info(f"[{task_id}] Démarrage extraction")
            task.current_step = "extraction"
            extract_dir = await self._extract_archive(upload_path, task_id)
            task.progress = 25.0
            await self._update_task_status(task_id, task)

            # Étape 2: Validation et organisation des fichiers audio
            logger.info(f"[{task_id}] Validation fichiers audio")
            task.current_step = "validation"
            audio_files = await self._validate_and_organize_audio_files(extract_dir)
            task.progress = 50.0
            await self._update_task_status(task_id, task)

            # Étape 3: Extraction des métadonnées
            logger.info(f"[{task_id}] Extraction métadonnées")
            task.current_step = "metadata"
            metadata = await self._extract_metadata_from_files(audio_files)
            task.metadata = asdict(metadata)
            task.progress = 75.0
            await self._update_task_status(task_id, task)

            # Étape 4: Conversion vers M4B (si nécessaire)
            logger.info(f"[{task_id}] Conversion M4B")
            task.current_step = "conversion"
            converted_files = await self._convert_to_m4b(
                audio_files, extract_dir, task_id
            )
            task.progress = 90.0
            await self._update_task_status(task_id, task)

            # Étape 5: Finalisation
            logger.info(f"[{task_id}] Finalisation")
            task.current_step = "completed"
            task.status = "completed"
            task.progress = 100.0
            await self._update_task_status(task_id, task)

            # Nettoyage (garder en cache pour récupération)
            await self._cleanup_task_files(task_id)

        except Exception as e:
            logger.error(f"[{task_id}] Erreur traitement: {str(e)}", exc_info=True)
            task.status = "failed"
            task.error_message = str(e)
            await self._update_task_status(task_id, task)

            # Nettoyer les fichiers en cas d'erreur
            await self._cleanup_task_files(task_id)
            raise

    async def get_task_status(
        self, task_id: str, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'une tâche.

        Args:
            task_id: ID de la tâche
            user_id: ID de l'utilisateur

        Returns:
            Statut de la tâche ou None si non trouvée
        """
        async with self._task_lock:
            task = self._tasks_cache.get(task_id)

        if not task or task.user_id != user_id:
            return None

        return asdict(task)

    async def check_task_ownership(self, task_id: str, user_id: int) -> bool:
        """
        Vérifie qu'une tâche appartient à l'utilisateur.

        Args:
            task_id: ID de la tâche
            user_id: ID de l'utilisateur

        Returns:
            True si la tâche existe et appartient à l'utilisateur
        """
        async with self._task_lock:
            task = self._tasks_cache.get(task_id)
            return task is not None and task.user_id == user_id

    async def cancel_task(self, task_id: str, user_id: int) -> bool:
        """
        Annule une tâche en cours.

        Args:
            task_id: ID de la tâche
            user_id: ID de l'utilisateur

        Returns:
            True si la tâche a été annulée
        """
        async with self._task_lock:
            task = self._tasks_cache.get(task_id)

        if not task or task.user_id != user_id:
            return False

        if task.status not in ["processing"]:
            return False

        task.status = "cancelled"
        task.error_message = "Tâche annulée par l'utilisateur"
        await self._update_task_status(task_id, task)
        await self._cleanup_task_files(task_id)

        return True

    async def retry_processing_task(
        self, task_id: str, user_id: int, db: Session
    ) -> None:
        """
        Relance une tâche échouée.

        Args:
            task_id: ID de la tâche
            user_id: ID de l'utilisateur
            db: Session de base de données
        """
        async with self._task_lock:
            task = self._tasks_cache.get(task_id)

        if not task or task.user_id != user_id:
            raise ProcessingError("Tâche non trouvée")

        if task.status != "failed":
            raise ProcessingError("Seules les tâches échouées peuvent être relancées")

        # TODO: Réimplémenter la logique de relance selon l'état d'échec
        logger.info(f"[{task_id}] Relance de la tâche")

    async def _extract_archive(self, archive_path: Path, task_id: str) -> Path:
        """
        Extrait une archive dans un répertoire temporaire.

        Args:
            archive_path: Chemin vers l'archive
            task_id: ID de la tâche

        Returns:
            Chemin vers le répertoire d'extraction

        Raises:
            ExtractionError: En cas d'erreur d'extraction
        """
        extract_dir = self.temp_dir / f"{task_id}_extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            file_ext = archive_path.suffix.lower()

            if file_ext == ".zip":
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif file_ext == ".rar":
                with rarfile.RarFile(archive_path, "r") as rar_ref:
                    rar_ref.extractall(extract_dir)
            else:
                # Utiliser patoolib pour les autres formats
                patoolib.extract_archive(str(archive_path), outdir=str(extract_dir))

            # Vérifier que des fichiers ont été extraits
            if not any(extract_dir.iterdir()):
                raise ExtractionError("Archive vide ou corrompue")

            logger.info(
                f"Archive extraite: {len(list(extract_dir.rglob('*')))} fichiers"
            )
            return extract_dir

        except Exception as e:
            logger.error(f"Erreur extraction archive: {e}")
            shutil.rmtree(extract_dir, ignore_errors=True)
            raise ExtractionError(f"Erreur lors de l'extraction: {str(e)}")

    async def _validate_and_organize_audio_files(self, extract_dir: Path) -> List[Path]:
        """
        Valide et organise les fichiers audio extraits.

        Args:
            extract_dir: Répertoire d'extraction

        Returns:
            Liste des fichiers audio valides

        Raises:
            ProcessingError: Si aucun fichier audio valide n'est trouvé
        """
        audio_files = []

        for file_path in extract_dir.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.SUPPORTED_AUDIO_FORMATS
            ):
                # Validation basique du fichier audio
                try:
                    audio = MutagenFile(file_path)
                    if (
                        audio is not None
                        and hasattr(audio, "info")
                        and audio.info.length > 0
                    ):
                        audio_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Fichier audio invalide ignoré: {file_path} - {e}")

        if not audio_files:
            raise ProcessingError("Aucun fichier audio valide trouvé dans l'archive")

        # Trier par nom de fichier (suppose un ordre logique)
        audio_files.sort(key=lambda x: x.name)

        logger.info(f"{len(audio_files)} fichiers audio validés")
        return audio_files

    async def _extract_metadata_from_files(
        self, audio_files: List[Path]
    ) -> AudioMetadata:
        """
        Extrait les métadonnées des fichiers audio.

        Args:
            audio_files: Liste des fichiers audio

        Returns:
            Métadonnées consolidées
        """
        metadata_list = []

        for file_path in audio_files:
            try:
                audio = MutagenFile(file_path)

                if audio is None:
                    continue

                # Extraire les métadonnées de base
                file_metadata = AudioMetadata()
                file_metadata.format = file_path.suffix.lower()[1:]  # Remove dot

                if hasattr(audio, "info"):
                    file_metadata.duration = audio.info.length
                    file_metadata.bitrate = getattr(audio.info, "bitrate", None)

                # Métadonnées ID3 spécifiques
                if hasattr(audio, "tags") and audio.tags:
                    tags = audio.tags

                    if hasattr(tags, "get"):
                        file_metadata.title = self._extract_id3_text(tags, "TIT2")
                        file_metadata.artist = self._extract_id3_text(
                            tags, "TPE1", "TPE2"
                        )
                        file_metadata.album = self._extract_id3_text(tags, "TALB")
                        file_metadata.year = self._extract_id3_text(
                            tags, "TDRC", "TYER"
                        )
                        file_metadata.track_number = self._extract_id3_text(
                            tags, "TRCK"
                        )
                        file_metadata.genre = self._extract_id3_text(tags, "TCON")

                metadata_list.append(file_metadata)

            except Exception as e:
                logger.warning(f"Erreur extraction métadonnées {file_path}: {e}")

        # Consolider les métadonnées (prendre la première valeur non nulle)
        consolidated = AudioMetadata()
        for meta in metadata_list:
            for field, value in asdict(meta).items():
                if value is not None and getattr(consolidated, field) is None:
                    setattr(consolidated, field, value)

        # Compter le nombre de fichiers
        consolidated.chapters = [
            {"title": f"Chapitre {i+1}", "start": i * 600}  # 10 min par fichier
            for i in range(len(audio_files))
        ]

        logger.info(
            f"Métadonnées extraites: {consolidated.title} - {consolidated.artist}"
        )
        return consolidated

    async def _convert_to_m4b(
        self, audio_files: List[Path], output_dir: Path, task_id: str, retry_count: int = 0
    ) -> List[Path]:
        """
        Convertit les fichiers audio vers le format M4B.

        Args:
            audio_files: Fichiers audio à convertir
            output_dir: Répertoire de sortie
            task_id: ID de la tâche

        Returns:
            Liste des fichiers convertis
        """
        converted_files = []

        # Si un seul fichier MP3, convertir directement
        if len(audio_files) == 1 and audio_files[0].suffix.lower() == ".mp3":
            output_file = output_dir / f"{task_id}.m4b"
            await self._convert_single_file(audio_files[0], output_file)
            converted_files.append(output_file)
        else:
            # Concaténer plusieurs fichiers en M4B
            concat_file = output_dir / f"{task_id}_concat.txt"
            output_file = output_dir / f"{task_id}.m4b"

            # Créer fichier de liste pour FFmpeg
            file_list = []
            for i, audio_file in enumerate(audio_files):
                if audio_file.suffix.lower() != ".m4b":
                    temp_converted = output_dir / f"temp_{i}.m4a"
                    await self._convert_single_file(audio_file, temp_converted)
                    file_list.append(f"file '{temp_converted.absolute()}'")
                else:
                    file_list.append(f"file '{audio_file.absolute()}'")

            with open(concat_file, "w", encoding="utf-8") as f:
                f.write("\n".join(file_list))

            # Concaténer avec FFmpeg
            cmd = [
                self.ffmpeg_path,
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(output_file),
            ]

            result = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode != 0:
                stderr = await result.stderr.read()
                raise ProcessingError(f"Erreur conversion FFmpeg: {stderr.decode()}")

            converted_files.append(output_file)

        logger.info(f"Conversion terminée: {len(converted_files)} fichier(s)")
        return converted_files

    async def _convert_single_file(self, input_file: Path, output_file: Path) -> None:
        """
        Convertit un fichier audio individuel vers M4A/M4B.

        Args:
            input_file: Fichier source
            output_file: Fichier de destination
        """
        cmd = [
            self.ffmpeg_path,
            "-i",
            str(input_file),
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(output_file),
        ]

        result = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await result.wait()

        if result.returncode != 0:
            stderr = await result.stderr.read()
            raise ProcessingError(f"Erreur conversion FFmpeg: {stderr.decode()}")

    def _extract_id3_text(self, tags, *tag_keys):
        """
        Extrait le texte d'un tag ID3 en essayant plusieurs clés.

        Args:
            tags: Tags ID3
            tag_keys: Clés à essayer dans l'ordre

        Returns:
            Texte du tag ou None
        """
        for key in tag_keys:
            try:
                tag = tags.get(key)
                if tag and hasattr(tag, "text"):
                    text = tag.text
                    if isinstance(text, list):
                        return text[0] if text else None
                    return str(text)
            except (KeyError, AttributeError):
                continue
        return None

    async def _update_task_status(self, task_id: str, task: UploadTask) -> None:
        """
        Met à jour le status d'une tâche dans le cache.

        Args:
            task_id: ID de la tâche
            task: Objet tâche mis à jour
        """
        async with self._task_lock:
            self._tasks_cache[task_id] = task

    async def _cleanup_task_files(self, task_id: str) -> None:
        """
        Nettoie les fichiers temporaires d'une tâche.

        Args:
            task_id: ID de la tâche
        """
        try:
            # Nettoyer les fichiers temporaires
            for pattern in [f"{task_id}_*", f"*{task_id}*"]:
                for path in self.temp_dir.glob(pattern):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)

            logger.info(f"[{task_id}] Nettoyage terminé")

        except Exception as e:
            logger.error(f"Erreur nettoyage {task_id}: {e}")

    async def _update_metadata_file(
        self, file_path: Path, metadata: AudioMetadata
    ) -> None:
        """
        Met à jour les métadonnées d'un fichier audio.

        Args:
            file_path: Chemin du fichier
            metadata: Métadonnées à appliquer
        """
        try:
            audio = MutagenFile(file_path, easy=True)

            if audio is None:
                return

            # Mise à jour des métadonnées de base
            if metadata.title:
                audio["title"] = metadata.title
            if metadata.artist:
                audio["artist"] = metadata.artist
            if metadata.album:
                audio["album"] = metadata.album
            if metadata.year:
                audio["year"] = metadata.year
            if metadata.track_number:
                audio["tracknumber"] = metadata.track_number
            if metadata.genre:
                audio["genre"] = metadata.genre

            audio.save()

            # Pour ID3, mise à jour spécifique si nécessaire
            if file_path.suffix.lower() in [".mp3"]:
                try:
                    id3 = ID3(file_path)

                    if metadata.title:
                        id3.add(TIT2(text=metadata.title))
                    if metadata.artist:
                        id3.add(TPE1(text=metadata.artist))
                    if metadata.album:
                        id3.add(TALB(text=metadata.album))
                    if metadata.year:
                        id3.add(TDRC(text=metadata.year))
                    if metadata.track_number:
                        id3.add(TRCK(text=metadata.track_number))
                    if metadata.genre:
                        id3.add(TCON(text=metadata.genre))

                    id3.save()
                except Exception as e:
                    logger.warning(f"Erreur mise à jour ID3: {e}")

            logger.info(f"Métadonnées mises à jour: {file_path.name}")

        except Exception as e:
            logger.error(f"Erreur mise à jour métadonnées {file_path}: {e}")
