"""
Service de planification pour la synchronisation automatique avec Audiobookshelf.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.audiobookshelf_instance import AudiobookshelfInstance
from app.services.audiobookshelf_sync import AudiobookshelfSyncService
from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService

logger = logging.getLogger(__name__)


class AudiobookshelfSchedulerService:
    """Service pour la planification automatique des synchronisations Audiobookshelf."""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.sync_service = AudiobookshelfSyncService(db=self.db)
        self.instance_service = AudiobookshelfInstanceService(self.db)
        self._running = False
        self._task = None

    def __del__(self):
        if hasattr(self, 'db') and self.db:
            self.db.close()

    async def start_scheduler(self) -> None:
        """
        Démarre le planificateur de synchronisation automatique.
        """
        if self._running:
            logger.warning("Le planificateur est déjà en cours d'exécution")
            return

        self._running = True
        logger.info("Démarrage du planificateur de synchronisation Audiobookshelf")

        try:
            await self._scheduler_loop()
        except Exception as e:
            logger.error(f"Erreur dans la boucle du planificateur: {str(e)}")
        finally:
            self._running = False

    async def stop_scheduler(self) -> None:
        """
        Arrête le planificateur de synchronisation automatique.
        """
        logger.info("Arrêt du planificateur de synchronisation")
        self._running = False

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _scheduler_loop(self) -> None:
        """
        Boucle principale du planificateur.
        """
        while self._running:
            try:
                await self._run_scheduled_syncs()
                # Attendre jusqu'à la prochaine exécution (toutes les heures)
                await asyncio.sleep(3600)  # 1 heure
            except Exception as e:
                logger.error(f"Erreur dans la boucle du planificateur: {str(e)}")
                await asyncio.sleep(60)  # Attendre 1 minute en cas d'erreur

    async def _run_scheduled_syncs(self) -> None:
        """
        Exécute les synchronisations planifiées pour toutes les instances actives.
        """
        logger.info("Début des synchronisations planifiées")

        instances = self.instance_service.get_instances(only_active=True)

        if not instances:
            logger.info("Aucune instance active trouvée pour la synchronisation")
            return

        sync_results = []

        for instance in instances:
            try:
                # Vérifier si une synchronisation est nécessaire
                if not self._should_sync_instance(instance):
                    continue

                logger.info(f"Synchronisation de l'instance {instance.name} (ID: {instance.id})")

                # Effectuer la synchronisation
                if self.sync_service.set_instance(instance.id):
                    result = self.sync_service.sync_all(full_sync=False)
                    sync_results.append({
                        'instance_id': instance.id,
                        'name': instance.name,
                        'success': result['errors'] == 0,
                        'stats': result
                    })

                    if result['errors'] > 0:
                        logger.warning(f"Synchronisation partiellement échouée pour {instance.name}: {result}")

                else:
                    logger.error(f"Impossible d'initialiser le client pour l'instance {instance.name}")
                    sync_results.append({
                        'instance_id': instance.id,
                        'name': instance.name,
                        'success': False,
                        'error': 'Client initialization failed'
                    })

            except Exception as e:
                logger.error(f"Erreur lors de la synchronisation de l'instance {instance.name}: {str(e)}")
                sync_results.append({
                    'instance_id': instance.id,
                    'name': instance.name,
                    'success': False,
                    'error': str(e)
                })

        self._log_sync_results(sync_results)
        logger.info("Fin des synchronisations planifiées")

    def _should_sync_instance(self, instance: AudiobookshelfInstance) -> bool:
        """
        Détermine si une instance doit être synchronisée.

        Args:
            instance: Instance à évaluer

        Returns:
            True si la synchronisation est nécessaire
        """
        now = datetime.utcnow()

        # Si pas de dernière synchronisation, synchroniser
        if not instance.last_sync:
            return True

        # Synchroniser si ça fait plus de 4 heures
        sync_interval = timedelta(hours=4)
        if now - instance.last_sync > sync_interval:
            return True

        # Synchroniser s'il y a eu des erreurs récentes
        if instance.status in ["error", "critical_error"] and instance.should_retry():
            return True

        return False

    async def sync_instance_now(self, instance_id: int) -> Dict:
        """
        Effectue une synchronisation immédiate pour une instance spécifique.

        Args:
            instance_id: ID de l'instance

        Returns:
            Résultat de la synchronisation
        """
        try:
            if self.sync_service.set_instance(instance_id):
                result = self.sync_service.sync_all(full_sync=False)
                return {
                    'success': result['errors'] == 0,
                    'stats': result
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initialize client'
                }
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation immédiate: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def full_sync_instance(self, instance_id: int) -> Dict:
        """
        Effectue une synchronisation complète pour une instance spécifique.

        Args:
            instance_id: ID de l'instance

        Returns:
            Résultat de la synchronisation
        """
        try:
            if self.sync_service.set_instance(instance_id):
                result = self.sync_service.sync_all(full_sync=True)
                return {
                    'success': result['errors'] == 0,
                    'stats': result
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initialize client'
                }
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation complète: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _log_sync_results(self, results: List[Dict]) -> None:
        """
        Log les résultats des synchronisations.

        Args:
            results: Liste des résultats
        """
        successful = len([r for r in results if r.get('success', False)])
        total = len(results)

        if total > 0:
            success_rate = (successful / total) * 100
            logger.info(f"Synchronisation terminée: {successful}/{total} réussies ({success_rate:.1f}%)")

            # Log détaillé des échecs
            failures = [r for r in results if not r.get('success', False)]
            for failure in failures:
                error = failure.get('error', 'Unknown error')
                logger.warning(f"Échec pour {failure.get('name', 'Unknown')}: {error}")

    def get_sync_status(self) -> Dict:
        """
        Retourne le statut actuel du planificateur et des instances.

        Returns:
            Statut du planificateur
        """
        instances = self.instance_service.get_instances()

        return {
            'scheduler_running': self._running,
            'total_instances': len(instances),
            'active_instances': len([i for i in instances if i.is_active]),
            'instances_with_errors': len([i for i in instances if i.status in ['error', 'critical_error']]),
            'instances_needing_sync': len([
                i for i in instances
                if i.is_active and self._should_sync_instance(i)
            ])
        }


class SyncTaskManager:
    """Gestionnaire des tâches de synchronisation en arrière-plan."""

    def __init__(self):
        self.scheduler = AudiobookshelfSchedulerService()
        self.task = None

    async def start_background_sync(self) -> None:
        """
        Démarre la synchronisation en arrière-plan.
        """
        if self.task and not self.task.done():
            logger.warning("La tâche de synchronisation est déjà en cours")
            return

        logger.info("Démarrage de la synchronisation en arrière-plan")
        self.task = asyncio.create_task(self.scheduler.start_scheduler())

    async def stop_background_sync(self) -> None:
        """
        Arrête la synchronisation en arrière-plan.
        """
        if self.task and not self.task.done():
            await self.scheduler.stop_scheduler()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        self.task = None
        logger.info("Synchronisation en arrière-plan arrêtée")

    def get_status(self) -> Dict:
        """
        Retourne le statut de la synchronisation.

        Returns:
            Statut actuel
        """
        return self.scheduler.get_sync_status()


# Instance globale pour la gestion des tâches
sync_manager = SyncTaskManager()


def get_sync_manager() -> SyncTaskManager:
    """
    Retourne l'instance globale du gestionnaire de synchronisation.

    Returns:
        Gestionnaire de synchronisation
    """
    return sync_manager


__all__ = ["AudiobookshelfSchedulerService", "SyncTaskManager", "get_sync_manager"]