from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.file_processing import FileProcessing as FileProcessingModel, ProcessingStatus
from app.schemas.file_processing import FileProcessingCreate, FileProcessingUpdate, ProcessingStatus as ProcessingStatusSchema

def get_file_processing(db: Session, file_id: int):
    """Récupère un fichier en traitement par son ID."""
    return db.query(FileProcessingModel).filter(FileProcessingModel.id == file_id).first()

def get_files_processing(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[ProcessingStatusSchema] = None,
    user_id: Optional[int] = None
):
    """Récupère une liste de fichiers en traitement avec filtrage optionnel."""
    query = db.query(FileProcessingModel)
    
    if status:
        query = query.filter(FileProcessingModel.status == status.value)
    if user_id is not None:
        query = query.filter(FileProcessingModel.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

def create_file_processing(db: Session, file_processing: FileProcessingCreate):
    """Crée une nouvelle entrée de fichier en traitement."""
    db_file = FileProcessingModel(**file_processing.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def update_file_processing(
    db: Session, 
    db_file: FileProcessingModel, 
    file_update: FileProcessingUpdate,
    update_modified: bool = True
):
    """Met à jour les informations d'un fichier en traitement."""
    update_data = file_update.dict(exclude_unset=True)
    
    if update_modified:
        update_data["updated_at"] = datetime.utcnow()
    
    # Mettre à jour la date de complétion si le statut est terminé ou échoué
    if file_update.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
        update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_file, field, value)
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def delete_file_processing(db: Session, file_id: int):
    """Supprime un fichier en traitement."""
    db_file = get_file_processing(db, file_id)
    if db_file:
        db.delete(db_file)
        db.commit()
    return db_file

def get_files_processing_by_status(
    db: Session, 
    status: ProcessingStatusSchema,
    skip: int = 0, 
    limit: int = 100
):
    """Récupère les fichiers en fonction de leur statut."""
    return db.query(FileProcessingModel).filter(
        FileProcessingModel.status == status.value
    ).offset(skip).limit(limit).all()

def update_file_progress(
    db: Session, 
    file_id: int, 
    progress: int,
    status: Optional[ProcessingStatusSchema] = None
):
    """Met à jour la progression d'un fichier en traitement."""
    db_file = get_file_processing(db, file_id)
    if not db_file:
        return None
    
    update_data = {"progress": progress, "updated_at": datetime.utcnow()}
    
    if status:
        update_data["status"] = status.value
        if status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_file, field, value)
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file
