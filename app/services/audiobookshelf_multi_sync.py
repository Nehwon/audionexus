"""
Service de synchronisation multi-instances Audiobookshelf.

Ce service gère la synchronisation bidirectionnelle entre plusieurs instances
Audiobookshelf avec détection et résolution automatique des conflits.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.audiobookshelf_sync import AudiobookshelfSyncService
from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService
from app.config import settings
from app.db.session import SessionLocal
from app.db.models.audiobook import Audiobook
from app.db.models.audiobookshelf_instance import AudiobookshelfInstance

logger = logging.getLogger(__name__)


@dataclass
class ConflictData:
    """Représente un conflit de données entre instances."""
    audiobook_id: str
    instance_a: int
    instance_b: int
    field: str
    value_a: any
    value_b: any
    timestamp_a: datetime
    timestamp_b: datetime

    def resolve_by_timestamp(self) -> Tuple[int, any]:
        """
        Résout le conflit basé sur le timestamp le plus récent.

        Returns:
            Tuple[int, any]: (instance_id gagnante, valeur gagnante)
        """
        if self.timestamp_a >= self.timestamp_b:
            return (self.instance_a, self.value_a)
        else:
            return (self.instance_b, self.value_b)


@dataclass
class SyncResult:
    """Résultat d'une opération de synchronisation."""
    instance_id: int
    instance_name: str
    success: bool
    synced_books: int
    conflicts_detected: int
    conflicts_resolved: int
    errors: List[str]
    duration_ms: int


class AudiobookshelfMultiSyncService:
    """Service de synchronisation multi-instances avec gestion des conflits."""

    def __init__(self, db: Session = None):
        """Initialise le service multi-sync."""
        self.db = db or SessionLocal()
        self.instance_service = AudiobookshelfInstanceService(self.db)
        self.conflict_resolution_strategy = "timestamp"  # timestamp, priority, manual

    def __del__(self):
        """Ferme la session de base de données."""
        if hasattr(self, 'db') and self.db:
            self.db.close()

    async def sync_all_instances(self, full_sync: bool = False) -> List[SyncResult]:
        """
        Synchronise toutes les instances actives de manière intelligente.

        Args:
            full_sync: Si True, force une synchronisation complète

        Returns:
            Liste des résultats de synchronisation
        """
        logger.info("Début de la synchronisation multi-instances")

        # Récupérer toutes les instances actives et synchronisables
        instances = self.instance_service.get_instances(
            only_active=True,
            only_sync_enabled=True
        )

        if not instances:
            logger.warning("Aucune instance active trouvée pour la synchronisation")
            return []

        # Exécuter les synchronisations en parallèle avec gestion des conflits
        tasks = []
        for instance in instances:
            task = self._sync_instance_smart(instance, full_sync)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Traiter les résultats
        sync_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                instance = instances[i]
                sync_results.append(SyncResult(
                    instance_id=instance.id,
                    instance_name=instance.name,
                    success=False,
                    synced_books=0,
                    conflicts_detected=0,
                    conflicts_resolved=0,
                    errors=[str(result)],
                    duration_ms=0
                ))
                logger.error(f"Erreur lors de la synchronisation de {instance.name}: {result}")
            else:
                sync_results.append(result)

        # Résoudre les conflits entre instances
        await self._resolve_cross_instance_conflicts(instances)

        logger.info(f"Synchronisation multi-instances terminée: {len(sync_results)} instances traitées")
        return sync_results

    async def _sync_instance_smart(self, instance: AudiobookshelfInstance, full_sync: bool) -> SyncResult:
        """
        Synchronise une instance de manière intelligente avec métriques.

        Args:
            instance: Instance à synchroniser
            full_sync: Synchronisation complète

        Returns:
            Résultat de la synchronisation
        """
        start_time = datetime.utcnow()

        try:
            # Créer un service de synchronisation pour cette instance
            sync_service = AudiobookshelfSyncService(db=self.db)

            if not sync_service.set_instance(instance.id):
                raise Exception(f"Impossible d'initialiser le client pour {instance.name}")

            # Exécuter la synchronisation
            if full_sync:
                stats = sync_service.initial_sync()
            else:
                stats = sync_service.sync_all()

            duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return SyncResult(
                instance_id=instance.id,
                instance_name=instance.name,
                success=True,
                synced_books=stats.get('audiobooks_synced', 0),
                conflicts_detected=0,  # Sera mis à jour lors de la résolution des conflits
                conflicts_resolved=0,
                errors=[],
                duration_ms=duration
            )

        except Exception as e:
            duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(f"Erreur lors de la synchronisation de {instance.name}: {str(e)}")

            return SyncResult(
                instance_id=instance.id,
                instance_name=instance.name,
                success=False,
                synced_books=0,
                conflicts_detected=0,
                conflicts_resolved=0,
                errors=[str(e)],
                duration_ms=duration
            )

    async def _resolve_cross_instance_conflicts(self, instances: List[AudiobookshelfInstance]):
        """
        Résout les conflits entre différentes instances.

        Args:
            instances: Liste des instances synchronisées
        """
        logger.info("Début de la résolution des conflits inter-instances")

        # Récupérer tous les audiobooks avec leurs métadonnées de synchronisation
        audiobooks = self._get_audiobooks_with_sync_data()

        conflicts_found = 0
        conflicts_resolved = 0

        for audiobook_data in audiobooks:
            conflicts = self._detect_conflicts(audiobook_data, instances)
            if conflicts:
                conflicts_found += len(conflicts)
                resolved = await self._resolve_conflicts(conflicts)
                conflicts_resolved += resolved

        logger.info(f"Résolution des conflits terminée: {conflicts_found} détectés, {conflicts_resolved} résolus")

    def _get_audiobooks_with_sync_data(self) -> List[Dict]:
        """
        Récupère les audiobooks avec leurs données de synchronisation.

        Returns:
            Liste des audiobooks avec métadonnées
        """
        # Cette méthode devrait récupérer les données depuis la base
        # Pour l'instant, retourner une liste vide (à implémenter selon le schéma réel)
        return []

    def _detect_conflicts(self, audiobook_data: Dict, instances: List[AudiobookshelfInstance]) -> List[ConflictData]:
        """
        Détecte les conflits pour un audiobook spécifique.

        Args:
            audiobook_data: Données de l'audiobook
            instances: Liste des instances

        Returns:
            Liste des conflits détectés
        """
        conflicts = []

        # Logique de détection de conflits basée sur les timestamps et valeurs
        # À implémenter selon les besoins spécifiques

        return conflicts

    async def _resolve_conflicts(self, conflicts: List[ConflictData]) -> int:
        """
        Résout une liste de conflits.

        Args:
            conflicts: Liste des conflits à résoudre

        Returns:
            Nombre de conflits résolus
        """
        resolved_count = 0

        for conflict in conflicts:
            try:
                if self.conflict_resolution_strategy == "timestamp":
                    winner_instance, winner_value = conflict.resolve_by_timestamp()
                elif self.conflict_resolution_strategy == "priority":
                    winner_instance, winner_value = await self._resolve_by_priority(conflict)
                else:
                    continue  # Pour "manual", ne pas résoudre automatiquement

                # Appliquer la résolution
                await self._apply_conflict_resolution(conflict, winner_instance, winner_value)
                resolved_count += 1

                logger.info(f"Conflit résolu pour {conflict.audiobook_id}.{conflict.field}: "
                          f"instance {winner_instance} gagnante")

            except Exception as e:
                logger.error(f"Erreur lors de la résolution du conflit {conflict.audiobook_id}: {str(e)}")

        return resolved_count

    async def _resolve_by_priority(self, conflict: ConflictData) -> Tuple[int, any]:
        """
        Résout un conflit basé sur la priorité des instances.

        Args:
            conflict: Conflit à résoudre

        Returns:
            Tuple[int, any]: (instance gagnante, valeur gagnante)
        """
        instance_a = self.instance_service.get_instance(conflict.instance_a)
        instance_b = self.instance_service.get_instance(conflict.instance_b)

        if instance_a.priority <= instance_b.priority:  # Priorité plus basse = plus haute priorité
            return (conflict.instance_a, conflict.value_a)
        else:
            return (conflict.instance_b, conflict.value_b)

    async def _apply_conflict_resolution(self, conflict: ConflictData, winner_instance: int, winner_value: any):
        """
        Applique la résolution d'un conflit.

        Args:
            conflict: Conflit résolu
            winner_instance: Instance gagnante
            winner_value: Valeur gagnante
        """
        # Appliquer la résolution dans la base de données et les instances
        # À implémenter selon le schéma de données réel
        pass

    def get_sync_status(self) -> Dict:
        """
        Retourne le statut général de la synchronisation multi-instances.

        Returns:
            Dict: Statut de synchronisation
        """
        instances = self.instance_service.get_instances(only_active=True, only_sync_enabled=True)

        total_instances = len(instances)
        healthy_instances = len([i for i in instances if i.status == "active"])
        unhealthy_instances = total_instances - healthy_instances

        return {
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "unhealthy_instances": unhealthy_instances,
            "average_health_score": sum(i.get_health_score() for i in instances) / max(total_instances, 1),
            "last_sync_check": datetime.utcnow().isoformat(),
            "conflict_resolution_strategy": self.conflict_resolution_strategy
        }