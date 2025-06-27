from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class ProcessingStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FileProcessing(Base):
    __tablename__ = "file_processing"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    status = Column(String, default=ProcessingStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    error_message = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    user = relationship("User", back_populates="processing_files")
