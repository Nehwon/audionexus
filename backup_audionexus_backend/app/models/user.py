from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.file_processing import ProcessingStatus

class User(Base):
    """Modèle utilisateur pour la base de données."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relations
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    processing_files: Mapped[List["FileProcessing"]] = relationship(
        "FileProcessing", 
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"

class RefreshToken(Base):
    """Modèle pour stocker les jetons de rafraîchissement."""
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self) -> str:
        return f"<RefreshToken {self.id} for user {self.user_id}>"

    @property
    def is_expired(self) -> bool:
        """Vérifie si le jeton est expiré."""
        return datetime.utcnow() >= self.expires_at
