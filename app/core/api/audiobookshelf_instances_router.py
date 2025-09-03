"""
Routes FastAPI pour la gestion des instances Audiobookshelf.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
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