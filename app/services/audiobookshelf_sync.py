"""
Service de synchronisation avec Audiobookshelf.

Ce service permet de maintenir une synchronisation entre la base de données locale
d'AudioNexus et le serveur Audiobookshelf distant.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.core.api.audiobookshelf import AudiobookshelfClient
from app.crud import audiobook as audiobook_crud
from app.crud import audiobookshelf_instance as instance_crud
from app.db.database import SessionLocal
from app.db.models.audiobook import Audiobook, AudiobookProgress
from app.schemas.audiobook import AudiobookCreate, AudiobookProgressCreate
from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService

# Configuration du logging
logger = logging.getLogger(__name__)


class AudiobookshelfSyncService:
    """Service de synchronisation avec Audiobookshelf."""

    def __init__(self, db: Session = None, instance_id: int = None):
        """Initialise le service de synchronisation.

        Args:
            db: Session de base de données
            instance_id: ID de l'instance Audiobookshelf à utiliser
        """
        self.db = db or SessionLocal()
        self.instance_id = instance_id
        self.instance_service = AudiobookshelfInstanceService(self.db)
        self.audioshelf_client = None

        # Initialiser le client si une instance est spécifiée
        if instance_id:
            self._init_client()

    def _init_client(self) -> bool:
        """Initialise le client Audiobookshelf avec l'instance sélectionnée."""
        if not self.instance_id:
            return False

        instance = self.instance_service.get_instance(self.instance_id)
        if not instance:
            logger.error(f"Instance Audiobookshelf {self.instance_id} non trouvée")
            return False

        if not instance.is_active:
            logger.warning(f"Instance Audiobookshelf {self.instance_id} est désactivée")
            return False

        try:
            token = self.instance_service.get_decrypted_token(self.instance_id)
            if not token:
                logger.error(
                    f"Impossible de récupérer le token pour l'instance {self.instance_id}"
                )
                return False

            self.audioshelf_client = AudiobookshelfClient(instance.base_url, token)
            return True

        except Exception as e:
            logger.error(
                f"Erreur lors de l'initialisation du client pour l'instance {self.instance_id}: {str(e)}"
            )
            return False

    def set_instance(self, instance_id: int) -> bool:
        """
        Définit l'instance partenaire à utiliser pour la synchronisation.

        Args:
            instance_id: ID de l'instance Audiobookshelf

        Returns:
            True si l'instance a été définie avec succès
        """
        self.instance_id = instance_id
        return self._init_client()

    def __del__(self):
        """Ferme la session de base de données lors de la destruction."""
        if hasattr(self, "db") and self.db:
            self.db.close()

    def sync_all(self, full_sync: bool = False) -> Dict[str, int]:
        """
        Effectue une synchronisation complète avec Audiobookshelf.

        Args:
            full_sync: Si True, force une synchronisation complète même si non nécessaire

        Returns:
            Dict: Statistiques de la synchronisation
        """
        stats = {
            "libraries_synced": 0,
            "audiobooks_synced": 0,
            "progress_updated": 0,
            "errors": 0,
        }

        # Vérifier si le client est initialisé
        if not self.audioshelf_client:
            logger.error(
                "Client Audiobookshelf non initialisé. Définissez d'abord une instance."
            )
            stats["errors"] += 1
            return stats

        try:
            # 1. Synchroniser les bibliothèques
            stats["libraries_synced"] = self.sync_libraries()

            # 2. Synchroniser les livres audio (avec traitement par page si nécessaire)
            stats["audiobooks_synced"] = self.sync_audiobooks(
                full_sync=full_sync, use_pagination=False
            )

            # 3. Synchroniser les progressions de lecture
            stats["progress_updated"] = self.sync_reading_progress()

            # 4. Mettre à jour la dernière synchronisation
            if self.instance_id:
                instance_crud.update_connection_status(
                    db=self.db, instance_id=self.instance_id, status="active"
                )

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {str(e)}", exc_info=True)
            stats["errors"] += 1

            # Marquer l'instance comme en erreur
            if self.instance_id:
                try:
                    self.instance_service.update_connection_status(
                        db=self.db,
                        instance_id=self.instance_id,
                        status="error",
                        error=str(e),
                    )
                except Exception as update_error:
                    logger.error(
                        f"Erreur lors de la mise à jour du statut: {update_error}"
                    )

        return stats

    def initial_sync(self, batch_size: int = 100) -> Dict[str, int]:
        """
        Effectue une synchronisation initiale complète d'une nouvelle instance.

        Args:
            batch_size: Nombre d'éléments à traiter par lot

        Returns:
            Statistiques de la synchronisation initiale
        """
        stats = {
            "libraries_synced": 0,
            "audiobooks_synced": 0,
            "total_pages": 0,
            "errors": 0,
        }

        # Vérifier si le client est initialisé
        if not self.audioshelf_client:
            logger.error("Client Audiobookshelf non initialisé.")
            stats["errors"] += 1
            return stats

        logger.info("Début de la synchronisation initiale complète")

        try:
            # 1. Synchroniser les bibliothèques d'abord
            stats["libraries_synced"] = self.sync_libraries()

            # 2. Synchronisation complète par pages
            audiobook_stats = self.sync_audiobooks_complete(batch_size=batch_size)
            stats.update(audiobook_stats)

            # 3. Synchroniser les progressions
            stats["progress_synced"] = self.sync_reading_progress()

            # 4. Marquer la synchronisation comme réussie
            if stats["errors"] == 0 and self.instance_id:
                instance_crud.update_connection_status(
                    db=self.db, instance_id=self.instance_id, status="active"
                )

            logger.info(f"Synchronisation initiale terminée: {stats}")

        except Exception as e:
            logger.error(
                f"Erreur lors de la synchronisation initiale: {str(e)}", exc_info=True
            )
            stats["errors"] += 1

        return stats

    def sync_audiobooks_complete(self, batch_size: int = 100) -> Dict[str, int]:
        """
        Synchronise tous les livres audio par pages pour éviter la surcharge mémoire.

        Args:
            batch_size: Nombre d'éléments par page

        Returns:
            Statistiques de synchronisation des livres audio
        """
        stats = {"audiobooks_synced": 0, "total_pages": 0, "errors": 0}

        try:
            # Récupérer les bibliothèques
            libraries = self.audioshelf_client.get_libraries()
            logger.info(f"Trouvé {len(libraries)} bibliothèques à synchroniser")

            for library in libraries:
                library_id = library.get("id")
                if not library_id:
                    continue

                logger.info(
                    f"Synchronisation de la bibliothèque: {library.get('name', library_id)}"
                )

                # Synchroniser par pages si l'API le supporte
                page = 1
                while True:
                    try:
                        # Pour simplifier, on utilise une recherche sans filtre pour tout récupérer
                        # Dans une vraie implémentation, on pourrait utiliser la pagination si disponible
                        items = self.audioshelf_client.search_library(
                            library_id, "", limit=batch_size
                        )
                        page_stats = self._process_audiobook_batch(items, library_id)

                        stats["audiobooks_synced"] += page_stats["processed"]
                        stats["total_pages"] += 1

                        page += 1
                        if len(items) < batch_size:
                            # Plus d'éléments à traiter
                            break

                    except Exception as e:
                        logger.error(
                            f"Erreur lors du traitement de la page {page} pour la bibliothèque {library_id}: {str(e)}"
                        )
                        stats["errors"] += 1
                        break

        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation complète: {str(e)}")
            stats["errors"] += 1

        return stats

    def _process_audiobook_batch(
        self, items: List[Dict], library_id: str
    ) -> Dict[str, int]:
        """
        Traite un lot d'éléments de livres audio.

        Args:
            items: Liste des éléments à traiter
            library_id: ID de la bibliothèque source

        Returns:
            Statistiques du traitement
        """
        stats = {"processed": 0, "updated": 0, "created": 0, "errors": 0}

        for item in items:
            try:
                # Vérifier si le livre existe déjà
                existing = audiobook_crud.get_audiobook_by_external_id(
                    self.db, external_id=item.get("id"), source="audiobookshelf"
                )

                # Préparer les données
                audiobook_data = self._map_audiobook_data(item, library_id)

                if existing:
                    # Mettre à jour le livre existant
                    audiobook_crud.update_audiobook(
                        self.db, db_obj=existing, obj_in=audiobook_data
                    )
                    stats["updated"] += 1
                else:
                    # Créer un nouveau livre
                    from app.schemas.audiobook import AudiobookCreate

                    audiobook_crud.create_audiobook(
                        self.db, obj_in=AudiobookCreate(**audiobook_data)
                    )
                    stats["created"] += 1

                stats["processed"] += 1

            except Exception as e:
                logger.error(
                    f"Erreur lors du traitement du livre {item.get('id')}: {str(e)}"
                )
                stats["errors"] += 1
                continue

        return stats

    def sync_libraries(self) -> int:
        """
        Synchronise les bibliothèques depuis Audiobookshelf.

        Returns:
            int: Nombre de bibliothèques synchronisées
        """
        try:
            libraries = self.audioshelf_client.get_libraries()
            # Ici, on pourrait enregistrer les bibliothèques en base si nécessaire
            return len(libraries)
        except Exception as e:
            logger.error(
                f"Erreur lors de la synchronisation des bibliothèques: {str(e)}"
            )
            return 0

    def sync_audiobooks(self, full_sync: bool = False) -> int:
        """
        Synchronise les livres audio depuis Audiobookshelf.

        Args:
            full_sync: Si True, force la synchronisation de tous les livres

        Returns:
            int: Nombre de livres audio synchronisés
        """
        synced_count = 0

        try:
            # Récupérer les bibliothèques
            libraries = self.audioshelf_client.get_libraries()

            for library in libraries:
                library_id = library.get("id")
                if not library_id:
                    continue

                # Récupérer les livres de la bibliothèque
                try:
                    # Dans un cas réel, on utiliserait la pagination
                    # Pour la simplicité, on se limite aux 100 premiers résultats
                    items = self.audioshelf_client.search_library(library_id, "")

                    for item in items[:100]:  # Limite pour l'exemple
                        try:
                            # Vérifier si le livre existe déjà
                            existing = audiobook_crud.get_audiobook_by_external_id(
                                self.db,
                                external_id=item.get("id"),
                                source="audiobookshelf",
                            )

                            if existing and not full_sync:
                                # Vérifier si une mise à jour est nécessaire
                                last_updated = datetime.fromisoformat(
                                    item.get("updatedAt", "").replace("Z", "+00:00")
                                )
                                if (
                                    existing.updated_at
                                    and existing.updated_at >= last_updated
                                ):
                                    continue

                            # Préparer les données pour la création/mise à jour
                            audiobook_data = self._map_audiobook_data(item, library_id)

                            if existing:
                                # Mettre à jour le livre existant
                                audiobook_crud.update_audiobook(
                                    self.db, db_obj=existing, obj_in=audiobook_data
                                )
                            else:
                                # Créer un nouveau livre
                                audiobook_crud.create_audiobook(
                                    self.db, obj_in=AudiobookCreate(**audiobook_data)
                                )

                            synced_count += 1

                        except Exception as e:
                            logger.error(
                                f"Erreur lors du traitement du livre {item.get('id')}: {str(e)}"
                            )
                            continue

                except Exception as e:
                    logger.error(
                        f"Erreur lors de la récupération des livres de la bibliothèque {library_id}: {str(e)}"
                    )
                    continue

        except Exception as e:
            logger.error(
                f"Erreur lors de la synchronisation des livres audio: {str(e)}"
            )

        return synced_count

    def sync_reading_progress(self) -> int:
        """
        Synchronise les progressions de lecture depuis Audiobookshelf.

        Returns:
            int: Nombre de progressions mises à jour
        """
        updated_count = 0

        try:
            # Dans une implémentation réelle, on récupérerait les utilisateurs depuis la base
            # Pour l'exemple, on suppose qu'on a une méthode pour récupérer les utilisateurs
            users = []  # À remplacer par la récupération des utilisateurs

            for user in users:
                user_id = user.get("id")
                if not user_id:
                    continue

                # Récupérer les progressions de l'utilisateur
                try:
                    # Dans une vraie implémentation, on utiliserait une méthode pour récupérer
                    # les progressions d'un utilisateur depuis Audiobookshelf
                    # progressions = self.audioshelf_client.get_user_progress(user_id)
                    progressions = []  # Remplacer par l'appel réel

                    for progress in progressions:
                        try:
                            book_id = progress.get("book_id")
                            if not book_id:
                                continue

                            # Vérifier si le livre existe
                            audiobook = audiobook_crud.get_audiobook_by_external_id(
                                self.db, external_id=book_id, source="audiobookshelf"
                            )

                            if not audiobook:
                                continue

                            # Vérifier si une progression existe déjà
                            existing_progress = audiobook_crud.get_user_progress(
                                self.db, user_id=user_id, audiobook_id=audiobook.id
                            )

                            progress_data = {
                                "user_id": user_id,
                                "audiobook_id": audiobook.id,
                                "progress": progress.get("progress", 0),
                                "current_time": progress.get("current_time", 0),
                                "is_finished": progress.get("is_finished", False),
                                "last_updated": datetime.utcnow(),
                            }

                            if existing_progress:
                                # Mettre à jour la progression existante
                                audiobook_crud.update_progress(
                                    self.db,
                                    db_obj=existing_progress,
                                    obj_in=progress_data,
                                )
                            else:
                                # Créer une nouvelle progression
                                audiobook_crud.create_progress(
                                    self.db,
                                    obj_in=AudiobookProgressCreate(**progress_data),
                                )

                            updated_count += 1

                        except Exception as e:
                            logger.error(
                                f"Erreur lors du traitement de la progression pour l'utilisateur {user_id}, livre {book_id}: {str(e)}"
                            )
                            continue

                except Exception as e:
                    logger.error(
                        f"Erreur lors de la récupération des progressions pour l'utilisateur {user_id}: {str(e)}"
                    )
                    continue

        except Exception as e:
            logger.error(
                f"Erreur lors de la synchronisation des progressions: {str(e)}"
            )

        return updated_count

    def _map_audiobook_data(self, item: Dict, library_id: str) -> Dict:
        """
        Convertit les données d'un livre d'Audiobookshelf au format de notre modèle.

        Args:
            item: Données du livre depuis l'API Audiobookshelf
            library_id: ID de la bibliothèque source

        Returns:
            Dict: Données du livre au format de notre modèle
        """
        # Extraire les métadonnées
        metadata = item.get("metadata", {})

        # Mapper les auteurs (peuvent être multiples)
        authors = []
        if isinstance(metadata.get("author"), list):
            authors = metadata["author"]
        elif metadata.get("author"):
            authors = [metadata["author"]]

        # Mapper les genres
        genres = []
        if isinstance(metadata.get("genres"), list):
            genres = metadata["genres"]

        # Mapper les séries
        series = []
        if isinstance(metadata.get("series"), list):
            series = [
                {"name": s.get("name", ""), "sequence": s.get("sequence", 0)}
                for s in metadata["series"]
                if s.get("name")
            ]

        # Calculer la durée totale en secondes
        duration = 0
        if metadata.get("duration"):
            try:
                # Supposer que la durée est au format "HH:MM:SS"
                parts = metadata["duration"].split(":")
                if len(parts) == 3:
                    duration = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except (ValueError, AttributeError):
                pass

        # Retourner les données mappées
        return {
            "external_id": item.get("id"),
            "source": "audiobookshelf",
            "library_id": library_id,
            "title": metadata.get("title", "Titre inconnu"),
            "subtitle": metadata.get("subtitle", ""),
            "authors": authors,
            "narrators": metadata.get("narrator", []),
            "description": metadata.get("description", ""),
            "publisher": metadata.get("publisher", ""),
            "publish_year": metadata.get("publishYear"),
            "genres": genres,
            "series": series,
            "language": metadata.get("language", "fr"),
            "isbn": metadata.get("isbn", ""),
            "duration": duration,
            "cover_path": item.get("coverPath", ""),
            "audio_path": item.get("audioPath", ""),
            "file_size": item.get("size", 0),
            "file_format": item.get("format", ""),
            "bitrate": item.get("bitrate", 0),
            "channels": item.get("channels", 2),
            "sample_rate": item.get("sampleRate", 44100),
            "is_explicit": metadata.get("explicit", False),
            "is_abridged": metadata.get("abridged", False),
            "tags": metadata.get("tags", []),
            "rating": metadata.get("rating", 0),
            "num_tracks": metadata.get("numTracks", 1),
            "track_number": metadata.get("trackNumber", 1),
            "disc_number": metadata.get("discNumber", 1),
            "created_at": datetime.fromisoformat(
                item.get("createdAt", "").replace("Z", "+00:00")
            ),
            "updated_at": datetime.fromisoformat(
                item.get("updatedAt", "").replace("Z", "+00:00")
            ),
        }
