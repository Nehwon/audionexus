"""
Routes FastAPI pour la gestion de la synchronisation Audiobookshelf.
"""
import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.audiobookshelf_sync import AudiobookshelfSyncService
from app.services.audiobookshelf_scheduler import get_sync_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audiobookshelf/sync", tags=["audiobookshelf-sync"])


@router.post("/instances/{instance_id}/sync")
async def sync_instance(
    instance_id: int,
    full_sync: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Lance une synchronisation pour une instance spécifique.

    Args:
        instance_id: ID de l'instance
        full_sync: Si True, force une synchronisation complète
        background_tasks: Gestionnaire de tâches en arrière-plan
        db: Session de base de données

    Returns:
        Résultat de la synchronisation ou tâche en arrière-plan
    """
    sync_service = AudiobookshelfSyncService(db=db)

    # Vérifier que l'instance existe et est active
    from app.crud.audiobookshelf_instance import crud_audiobookshelf_instance
    instance = crud_audiobookshelf_instance.get(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    if not instance.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Instance {instance_id} est désactivée"
        )

    async def run_sync():
        """Fonction pour exécuter la synchronisation en arrière-plan."""
        try:
            if sync_service.set_instance(instance_id):
                if full_sync:
                    result = sync_service.initial_sync()
                else:
                    result = sync_service.sync_all()
                logger.info(f"Synchronisation{' complète' if full_sync else ''} terminée pour l'instance {instance_id}: {result}")
            else:
                logger.error(f"Impossible d'initialiser le client pour l'instance {instance_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation de l'instance {instance_id}: {str(e)}")

    # Lancer la synchronisation en arrière-plan
    background_tasks.add_task(run_sync)

    return {
        "message": f"Synchronisation {'complète' if full_sync else 'incrémentielle'} lancée pour l'instance {instance.name}",
        "instance_id": instance_id,
        "instance_name": instance.name,
        "sync_type": "full" if full_sync else "incremental"
    }


@router.post("/sync-all")
async def sync_all_instances(
    full_sync: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict:
    """
    Lance la synchronisation pour toutes les instances actives.

    Args:
        full_sync: Si True, force une synchronisation complète
        background_tasks: Gestionnaire de tâches en arrière-plan

    Returns:
        Confirmation du lancement
    """
    sync_manager = get_sync_manager()

    async def run_all_syncs():
        """Fonction pour synchroniser toutes les instances."""
        from app.db.session import SessionLocal
        from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService

        db = SessionLocal()
        try:
            instance_service = AudiobookshelfInstanceService(db)
            instances = instance_service.get_instances(only_active=True)

            for instance in instances:
                try:
                    if sync_manager.scheduler.sync_service.set_instance(instance.id):
                        if full_sync:
                            result = sync_manager.scheduler.sync_service.initial_sync()
                        else:
                            result = sync_manager.scheduler.sync_service.sync_all()

                        logger.info(f"Synchronisation terminée pour {instance.name}: {result}")
                    else:
                        logger.error(f"Échec d'initialisation pour {instance.name}")
                except Exception as e:
                    logger.error(f"Erreur lors de la synchronisation de {instance.name}: {str(e)}")
        finally:
            db.close()

    # Lancer en arrière-plan
    background_tasks.add_task(run_all_syncs)

    return {
        "message": f"Synchronisation {'complète' if full_sync else 'incrémentielle'} lancée pour toutes les instances actives",
        "sync_type": "full" if full_sync else "incremental"
    }


@router.get("/status")
async def get_sync_status() -> Dict:
    """
    Retourne le statut de la synchronisation automatique.

    Returns:
        Statut du système de synchronisation
    """
    sync_manager = get_sync_manager()
    return sync_manager.get_status()


@router.post("/scheduler/start")
async def start_scheduler(
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict:
    """
    Démarre le planificateur de synchronisation automatique.

    Args:
        background_tasks: Gestionnaire de tâches en arrière-plan

    Returns:
        Confirmation du démarrage
    """
    import asyncio

    sync_manager = get_sync_manager()

    async def start_scheduler_task():
        await sync_manager.start_background_sync()

    background_tasks.add_task(start_scheduler_task)

    return {
        "message": "Planificateur de synchronisation démarré",
        "status": "starting"
    }


@router.post("/scheduler/stop")
async def stop_scheduler() -> Dict:
    """
    Arrête le planificateur de synchronisation automatique.

    Returns:
        Confirmation de l'arrêt
    """
    import asyncio

    async def stop():
        sync_manager = get_sync_manager()
        await sync_manager.stop_background_sync()

    # Arrêter immédiatement (cette opération peut prendre du temps)
    asyncio.create_task(stop())

    return {
        "message": "Arrêt du planificateur de synchronisation demandé",
        "status": "stopping"
    }


@router.post("/instances/{instance_id}/initial-sync")
async def initial_sync_instance(
    instance_id: int,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Effectue une synchronisation initiale complète d'une nouvelle instance.

    Args:
        instance_id: ID de l'instance
        background_tasks: Gestionnaire de tâches en arrière-plan
        db: Session de base de données

    Returns:
        Confirmation du lancement
    """
    # Vérifier que l'instance existe
    from app.crud.audiobookshelf_instance import crud_audiobookshelf_instance
    instance = crud_audiobookshelf_instance.get(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    sync_service = AudiobookshelfSyncService(db=db)

    async def run_initial_sync():
        """Fonction pour exécuter la synchronisation initiale."""
        try:
            if sync_service.set_instance(instance_id):
                result = sync_service.initial_sync()
                logger.info(f"Synchronisation initiale terminée pour {instance.name}: {result}")
            else:
                logger.error(f"Impossible d'initialiser le client pour {instance.name}")
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation initiale de {instance.name}: {str(e)}")

    # Lancer en arrière-plan
    background_tasks.add_task(run_initial_sync)

    return {
        "message": f"Synchronisation initiale lancée pour l'instance {instance.name}",
        "instance_id": instance_id,
        "instance_name": instance.name
    }


@router.get("/instances/{instance_id}/progress")
async def get_sync_progress(instance_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Récupère les informations de progression de synchronisation d'une instance.

    Args:
        instance_id: ID de l'instance
        db: Session de base de données

    Returns:
        Informations de progression
    """
    from app.crud.audiobookshelf_instance import crud_audiobookshelf_instance
    instance = crud_audiobookshelf_instance.get(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    # Statistiques des livres audio synchronisés
    from app.crud.audiobook import crud_audiobook
    audiobook_count = crud_audiobook.get_multi_by_library(
        db,
        library_external_id=str(instance_id),  # À adapter selon le mapping réel
        count_only=True
    )

    return {
        "instance_id": instance_id,
        "name": instance.name,
        "last_sync": instance.last_sync.isoformat() if instance.last_sync else None,
        "status": instance.status,
        "synced_audiobooks": audiobook_count,
        "last_error": instance.last_error,
        "last_error_at": instance.last_error_at.isoformat() if instance.last_error_at else None
    }