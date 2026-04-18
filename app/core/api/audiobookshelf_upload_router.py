"""
Routeur pour la gestion des téléversements d'audiobooks.
Gère l'upload, la validation et le traitement automatique des archives audio.
"""

import logging
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.upload_service import (
    ExtractionError,
    ProcessingError,
    UploadService,
    UploadValidationError,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration du service d'upload
upload_service = UploadService()


@router.post("/upload", response_model=Dict[str, Any])
async def upload_audiobook_archive(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Téléverse et traite automatiquement une archive d'audiobook (ZIP/RAR).

    Args:
        file: L'archive à traiter (ZIP ou RAR)
        background_tasks: Gestionnaire de tâches asynchrones
        db: Session de base de données
        current_user: Utilisateur authentifié

    Returns:
        Dict contenant l'ID de tâche et les informations initiales

    Raises:
        HTTPException: En cas d'erreur de validation ou traitement
    """
    try:
        # Validation initiale du fichier
        await upload_service.validate_upload(file)

        # Création d'un identifiant unique pour cette tâche
        task_id = str(uuid.uuid4())

        # Enregistrement temporaire du fichier
        upload_path = await upload_service.save_temporary_file(file, task_id)

        # Lancement du traitement en arrière-plan
        background_tasks.add_task(
            upload_service.process_audiobook_archive,
            task_id=task_id,
            upload_path=upload_path,
            user_id=current_user.id,
            db=db,
        )

        logger.info(
            f"Upload démarré pour l'utilisateur {current_user.id}, tâche {task_id}"
        )

        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Traitement de l'archive commencé",
            "filename": file.filename,
        }

    except UploadValidationError as e:
        logger.error(f"Erreur de validation upload: {e.detail}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.detail)
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du traitement de l'upload",
        )


@router.get("/upload/status/{task_id}")
async def get_upload_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Récupère le statut d'une tâche d'upload.

    Args:
        task_id: Identifiant de la tâche
        db: Session de base de données
        current_user: Utilisateur authentifié

    Returns:
        Statut actuel de la tâche
    """
    try:
        status_data = await upload_service.get_task_status(task_id, current_user.id)

        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tâche non trouvée"
            )

        return status_data

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération du statut",
        )


@router.post("/upload/{task_id}/retry")
async def retry_upload(
    task_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Relance une tâche d'upload échouée.

    Args:
        task_id: Identifiant de la tâche à relancer
        background_tasks: Gestionnaire de tâches asynchrones
        db: Session de base de données
        current_user: Utilisateur authentifié

    Returns:
        Confirmation de relance
    """
    try:
        # Vérification que la tâche appartient à l'utilisateur
        task_exists = await upload_service.check_task_ownership(
            task_id, current_user.id
        )

        if not task_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tâche non trouvée ou accès non autorisé",
            )

        # Relance du traitement
        background_tasks.add_task(
            upload_service.retry_processing_task,
            task_id=task_id,
            user_id=current_user.id,
            db=db,
        )

        return {
            "task_id": task_id,
            "status": "restarting",
            "message": "Relance du traitement en cours",
        }

    except Exception as e:
        logger.error(f"Erreur lors de la relance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la relance du traitement",
        )


@router.delete("/upload/{task_id}")
async def cancel_upload(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Annule une tâche d'upload en cours.

    Args:
        task_id: Identifiant de la tâche à annuler
        db: Session de base de données
        current_user: Utilisateur authentifié

    Returns:
        Confirmation d'annulation
    """
    try:
        # Vérification et annulation de la tâche
        cancelled = await upload_service.cancel_task(task_id, current_user.id)

        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tâche non trouvée ou déjà terminée",
            )

        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Tâche annulée avec succès",
        }

    except Exception as e:
        logger.error(f"Erreur lors de l'annulation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'annulation",
        )
