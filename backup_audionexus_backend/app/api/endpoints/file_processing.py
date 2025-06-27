from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services import file_processing as file_processing_service
from app.schemas.file_processing import ProcessingStatus

router = APIRouter()

@router.get("/", response_model=List[schemas.FileProcessing])
def read_files_processing(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[ProcessingStatus] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Récupère une liste de fichiers en traitement.
    """
    # Seuls les administrateurs peuvent voir tous les fichiers
    if current_user.is_superuser:
        files = file_processing_service.get_files_processing(
            db, skip=skip, limit=limit, status=status
        )
    else:
        # Les utilisateurs normaux ne voient que leurs propres fichiers
        files = file_processing_service.get_files_processing(
            db, skip=skip, limit=limit, status=status, user_id=current_user.id
        )
    return files

@router.post("/", response_model=schemas.FileProcessing, status_code=status.HTTP_201_CREATED)
def create_file_processing(
    *,
    db: Session = Depends(deps.get_db),
    file_in: schemas.FileProcessingCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Crée une nouvelle entrée de fichier en traitement.
    """
    # S'assurer que l'utilisateur ne peut créer que pour lui-même
    if file_in.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return file_processing_service.create_file_processing(
        db=db, file_processing=file_in
    )

@router.get("/{file_id}", response_model=schemas.FileProcessing)
def read_file_processing(
    file_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Récupère un fichier en traitement par son ID.
    """
    db_file = file_processing_service.get_file_processing(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File processing not found")
    
    # Vérifier les permissions
    if db_file.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return db_file

@router.put("/{file_id}", response_model=schemas.FileProcessing)
def update_file_processing(
    *,
    db: Session = Depends(deps.get_db),
    file_id: int,
    file_in: schemas.FileProcessingUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Met à jour un fichier en traitement.
    """
    db_file = file_processing_service.get_file_processing(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File processing not found")
    
    # Vérifier les permissions
    if db_file.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return file_processing_service.update_file_processing(
        db=db, db_file=db_file, file_update=file_in
    )

@router.delete("/{file_id}", response_model=schemas.FileProcessing)
def delete_file_processing(
    *,
    db: Session = Depends(deps.get_db),
    file_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Supprime un fichier en traitement.
    """
    db_file = file_processing_service.get_file_processing(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File processing not found")
    
    # Vérifier les permissions
    if db_file.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return file_processing_service.delete_file_processing(db=db, file_id=file_id)

@router.put("/{file_id}/progress", response_model=schemas.FileProcessing)
def update_file_progress(
    *,
    db: Session = Depends(deps.get_db),
    file_id: int,
    progress: int,
    status: Optional[ProcessingStatus] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Met à jour la progression d'un fichier en traitement.
    """
    db_file = file_processing_service.get_file_processing(db, file_id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File processing not found")
    
    # Vérifier les permissions
    if db_file.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return file_processing_service.update_file_progress(
        db=db, file_id=file_id, progress=progress, status=status
    )
