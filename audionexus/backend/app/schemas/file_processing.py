from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Shared properties
class FileProcessingBase(BaseModel):
    filename: str
    original_path: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: int = Field(0, ge=0, le=100)
    error_message: Optional[str] = None
    user_id: int

# Properties to receive on item creation
class FileProcessingCreate(FileProcessingBase):
    pass

# Properties to receive on item update
class FileProcessingUpdate(BaseModel):
    status: Optional[ProcessingStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None

# Properties shared by models stored in DB
class FileProcessingInDBBase(FileProcessingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class FileProcessing(FileProcessingInDBBase):
    pass

# Properties stored in DB
class FileProcessingInDB(FileProcessingInDBBase):
    pass
