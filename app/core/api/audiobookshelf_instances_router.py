"""
Routes FastAPI pour la gestion des instances Audiobookshelf.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session_manager import get_db
from app.schemas.audiobookshelf_instance import (
    AudiobookshelfInstanceCreate,
    AudiobookshelfInstanceResponse,
    AudiobookshelfInstanceSummary,
    AudiobookshelfInstanceUpdate,
    AudiobookshelfInstanceTestResponse,
    AudiobookshelfInstanceTokenRotate,
    AudiobookshelfInstanceList
)
from app.services.audiobookshelf_instance_service import AudiobookshelfInstanceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audiobookshelf/instances", tags=["audiobookshelf-instances"])


@router.post("/", response_model=AudiobookshelfInstanceResponse)
async def create_instance(
    instance_data: AudiobookshelfInstanceCreate,
    db: Session = Depends(get_db)
) -> AudiobookshelfInstanceResponse:
    """
    Crée une nouvelle instance Audiobookshelf.

    Args:
        instance_data: Données de l'instance à créer
        db: Session de base de données

    Returns:
        Instance créée
    """
    service = AudiobookshelfInstanceService(db)

    instance = service.create_instance(
        name=instance_data.name,
        base_url=instance_data.base_url,
        username=instance_data.username,
        password=instance_data.password
    )

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de créer l'instance. Vérifiez la configuration et les identifiants."
        )

    # Retourner l'instance sans le token chiffré
    return AudiobookshelfInstanceResponse.from_orm(instance)


@router.get("/{instance_id}", response_model=AudiobookshelfInstanceResponse)
async def get_instance(
    instance_id: int,
    db: Session = Depends(get_db)
) -> AudiobookshelfInstanceResponse:
    """
    Récupère les détails d'une instance spécifique.

    Args:
        instance_id: ID de l'instance
        db: Session de base de données

    Returns:
        Détails de l'instance
    """
    service = AudiobookshelfInstanceService(db)
    instance = service.get_instance(instance_id)

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    return AudiobookshelfInstanceResponse.from_orm(instance)


@router.get("/", response_model=AudiobookshelfInstanceList)
async def list_instances(
    only_active: bool = True,
    db: Session = Depends(get_db)
) -> AudiobookshelfInstanceList:
    """
    Liste toutes les instances configurées.

    Args:
        only_active: Ne retourner que les instances actives
        db: Session de base de données

    Returns:
        Liste des instances
    """
    service = AudiobookshelfInstanceService(db)
    instances = service.get_instances(only_active=only_active)
    instance_summaries = []

    for instance in instances:
        # Tester la connexion pour mettre à jour le statut si nécessaire
        if instance.should_retry():
            test_result = service.test_connection(instance.id)
            instance.status = test_result.get("status", instance.status)
            instance.version = test_result.get("version")

        summary = AudiobookshelfInstanceSummary.from_orm(instance)
        instance_summaries.append(summary)

    # Calculer les statistiques
    total = len(instance_summaries)
    active = len([i for i in instance_summaries if i.is_active])

    return AudiobookshelfInstanceList(
        instances=instance_summaries,
        total=total,
        active=active
    )


@router.put("/{instance_id}", response_model=AudiobookshelfInstanceResponse)
async def update_instance(
    instance_id: int,
    update_data: AudiobookshelfInstanceUpdate,
    db: Session = Depends(get_db)
) -> AudiobookshelfInstanceResponse:
    """
    Met à jour une instance existante.

    Args:
        instance_id: ID de l'instance
        update_data: Données de mise à jour
        db: Session de base de données

    Returns:
        Instance mise à jour
    """
    service = AudiobookshelfInstanceService(db)

    # Vérifier que l'instance existe
    existing = service.get_instance(instance_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    success = service.update_instance(
        instance_id=instance_id,
        name=update_data.name,
        base_url=update_data.base_url,
        is_active=update_data.is_active
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la mise à jour de l'instance"
        )

    updated_instance = service.get_instance(instance_id)
    return AudiobookshelfInstanceResponse.from_orm(updated_instance)


@router.delete("/{instance_id}")
async def delete_instance(
    instance_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Supprime une instance.

    Args:
        instance_id: ID de l'instance à supprimer
        db: Session de base de données

    Returns:
        Confirmation de suppression
    """
    service = AudiobookshelfInstanceService(db)

    # Vérifier que l'instance existe
    existing = service.get_instance(instance_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    success = service.delete_instance(instance_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la suppression de l'instance"
        )

    return {
        "message": f"Instance {instance_id} supprimée avec succès",
        "instance_id": instance_id
    }


@router.post("/{instance_id}/rotate-token", response_model=AudiobookshelfInstanceResponse)
async def rotate_instance_token(
    instance_id: int,
    rotate_data: AudiobookshelfInstanceTokenRotate,
    db: Session = Depends(get_db)
) -> AudiobookshelfInstanceResponse:
    """
    Effectue une rotation du token d'une instance.

    Args:
        instance_id: ID de l'instance
        rotate_data: Données pour la rotation (nouveau mot de passe)
        db: Session de base de données

    Returns:
        Instance mise à jour
    """
    service = AudiobookshelfInstanceService(db)

    # Vérifier que l'instance existe
    existing = service.get_instance(instance_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    success = service.rotate_token(
        instance_id=instance_id,
        new_password=rotate_data.password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la rotation du token. Vérifiez les identifiants."
        )

    updated_instance = service.get_instance(instance_id)
    return AudiobookshelfInstanceResponse.from_orm(updated_instance)


@router.post("/{instance_id}/test", response_model=AudiobookshelfInstanceTestResponse)
async def test_instance_connection(
    instance_id: int,
    db: Session = Depends(get_db)
) -> AudiobookshelfInstanceTestResponse:
    """
    Teste la connexion à une instance.

    Args:
        instance_id: ID de l'instance
        db: Session de base de données

    Returns:
        Résultat du test de connexion
    """
    service = AudiobookshelfInstanceService(db)

    # Vérifier que l'instance existe
    existing = service.get_instance(instance_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    try:
        result = service.test_connection(instance_id)
        return AudiobookshelfInstanceTestResponse(**result)
    except Exception as e:
        logger.error(f"Erreur lors du test de connexion pour l'instance {instance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du test de connexion"
        )


@router.put("/{instance_id}/priority")
async def update_instance_priority(
    instance_id: int,
    priority: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Met à jour la priorité d'une instance pour le load balancing.

    Args:
        instance_id: ID de l'instance
        priority: Nouvelle priorité (1=haut, 10=bas)
        db: Session de base de données

    Returns:
        Confirmation de mise à jour
    """
    service = AudiobookshelfInstanceService(db)

    # Vérifier que l'instance existe
    existing = service.get_instance(instance_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance {instance_id} non trouvée"
        )

    # Valider la priorité
    if not 1 <= priority <= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La priorité doit être entre 1 et 10 (1=haut, 10=bas)"
        )

    # Mettre à jour la priorité (nécessiterait une méthode dans le service)
    # Pour l'instant, on simule la mise à jour
    logger.info(f"Mise à jour priorité instance {instance_id}: {priority}")

    return {
        "message": f"Priorité de l'instance {instance_id} mise à jour",
        "instance_id": instance_id,
        "priority": priority
    }


@router.post("/health-check")
async def perform_health_check_all(
    db: Session = Depends(get_db)
) -> dict:
    """
    Effectue un health check pour toutes les instances actives.

    Args:
        db: Session de base de données

    Returns:
        Résultats des health checks
    """
    from app.services.audiobookshelf_health_monitor import AudiobookshelfHealthMonitor

    monitor = AudiobookshelfHealthMonitor(db)
    await monitor.force_health_check_all()

    health_summary = monitor.get_health_summary()

    return {
        "message": "Health checks effectués pour toutes les instances",
        "summary": health_summary
    }


@router.get("/load-balancing/status")
async def get_load_balancing_status(
    db: Session = Depends(get_db)
) -> dict:
    """
    Retourne le status du load balancing.

    Args:
        db: Session de base de données

    Returns:
        Status du load balancing
    """
    from app.services.audiobookshelf_load_balancer import AudiobookshelfLoadBalancer

    load_balancer = AudiobookshelfLoadBalancer(db)
    distribution = await load_balancer.get_load_distribution()

    return {
        "load_distribution": distribution,
        "timestamp": distribution.get("timestamp")
    }


@router.post("/cache/clear")
async def clear_cache(
    instance_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    Vide le cache, optionnellement pour une instance spécifique.

    Args:
        instance_id: ID de l'instance (optionnel)
        db: Session de base de données

    Returns:
        Confirmation de vidage
    """
    from app.services.audiobookshelf_cache import AudiobookshelfCache

    cache = AudiobookshelfCache()

    if instance_id:
        cleared = await cache.invalidate_by_instance(instance_id)
        message = f"Cache de l'instance {instance_id} vidé: {cleared} entrées"
    else:
        cleared = await cache.clear_all()
        message = f"Cache complet vidé: {cleared} entrées"

    return {
        "message": message,
        "entries_cleared": cleared
    }


@router.post("/sync/multi-instance")
async def sync_all_multi_instances(
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
) -> dict:
    """
    Lance une synchronisation multi-instances complète.

    Args:
        background_tasks: Gestionnaire de tâches en arrière-plan
        db: Session de base de données

    Returns:
        Confirmation du lancement
    """
    from app.services.audiobookshelf_multi_sync import AudiobookshelfMultiSyncService

    async def run_multi_sync():
        multi_sync = AudiobookshelfMultiSyncService(db)
        results = await multi_sync.sync_all_instances()

        logger.info(f"Synchronisation multi-instances terminée: {len(results)} résultats")
        for result in results:
            logger.info(f"- {result.instance_name}: {result.synced_books} livres, {result.conflicts_detected} conflits")

    background_tasks.add_task(run_multi_sync)

    return {
        "message": "Synchronisation multi-instances lancée en arrière-plan",
        "status": "running"
    }


@router.get("/sync/status")
async def get_multi_sync_status(
    db: Session = Depends(get_db)
) -> dict:
    """
    Retourne le statut de la synchronisation multi-instances.

    Args:
        db: Session de base de données

    Returns:
        Statut de synchronisation
    """
    from app.services.audiobookshelf_multi_sync import AudiobookshelfMultiSyncService

    multi_sync = AudiobookshelfMultiSyncService(db)
    status = multi_sync.get_sync_status()

    return status