"""
Modèles de base de données SQLAlchemy pour l'application de gestion d'audiobooks.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

# Import de l'instance Base partagée
from app.db.database import Base  # noqa: F401

# Note: Tous les modèles doivent importer Base depuis ce module
# pour s'assurer qu'ils sont enregistrés avec la même instance de Base

# Table d'association pour la relation many-to-many entre utilisateurs et rôles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    extend_existing=True,
)

# Table d'association pour la relation many-to-many entre livres et étiquettes
book_tags = Table(
    "book_tags",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
    extend_existing=True,
)


class User(Base):
    """Modèle utilisateur pour l'authentification et l'autorisation."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    # Métadonnées étendues
    phone_number = Column(String(20))
    bio = Column(Text)
    avatar_url = Column(String(255))
    preferred_language = Column(String(10), default="fr")
    timezone = Column(String(50), default="Europe/Paris")
    custom_metadata = Column(JSON, default=dict)  # Données personnalisables
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))

    # Relations
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    books = relationship("Book", back_populates="owner")
    libraries = relationship("Library", back_populates="owner")
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User '{self.username}'>"

    def is_account_locked(self) -> bool:
        """Vérifie si le compte est verrouillé."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def record_login_attempt(self, success: bool = True):
        """Enregistre une tentative de connexion."""
        if success:
            self.login_attempts = 0
            self.locked_until = None
        else:
            self.login_attempts = (self.login_attempts or 0) + 1
            # Verrouiller le compte après 5 tentatives échouées
            if self.login_attempts >= 5:
                from datetime import timedelta

                self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        self.last_seen = datetime.utcnow()

    def set_password(self, password: str):
        """Définit le mot de passe de l'utilisateur."""
        from app.core.security import get_password_hash

        self.hashed_password = get_password_hash(password)
        return self

    def check_password(self, password: str) -> bool:
        """Vérifie si le mot de passe fourni correspond au hachage stocké."""
        from app.core.security import verify_password

        return verify_password(password, self.hashed_password)

    @property
    def password(self) -> str:
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password: str):
        """Définit le mot de passe de l'utilisateur (alias pour set_password)."""
        self.set_password(password)

    def to_dict(self) -> dict:
        """Convertit l'utilisateur en dictionnaire."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "phone_number": self.phone_number,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "preferred_language": self.preferred_language,
            "timezone": self.timezone,
            "custom_metadata": self.custom_metadata or {},
            "email_verified": self.email_verified,
            "two_factor_enabled": self.two_factor_enabled,
            "login_attempts": self.login_attempts,
            "locked_until": (
                self.locked_until.isoformat() if self.locked_until else None
            ),
        }

    @property
    def avatar(self) -> str:
        """Génère une URL d'avatar basée sur l'email de l'utilisateur."""
        import hashlib
        from urllib.parse import quote, quote_plus

        # Utilisation de Gravatar pour les avatars
        email_hash = hashlib.md5(self.email.lower().encode("utf-8")).hexdigest()

        # Créer une URL par défaut avec le nom d'utilisateur
        default_url = "https://ui-avatars.com/api/"
        name = quote(self.username.encode("utf-8"))
        default = f"{default_url}?name={name}&background=random"

        # Encoder l'URL par défaut pour l'utiliser comme paramètre
        encoded_default = quote_plus(default)

        return f"https://www.gravatar.com/avatar/{email_hash}?d={encoded_default}&s=200"


class Role(Base):
    """Modèle de rôles pour les utilisateurs."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))

    # Relations
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )


class Permission(Base):
    """Modèle de permissions granulaire pour le système d'autorisation."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    codename = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255))
    resource = Column(String(50), nullable=False)  # users, books, settings, etc.
    action = Column(String(20), nullable=False)  # create, read, update, delete, admin


class RolePermission(Base):
    """Table d'association many-to-many entre rôles et permissions."""

    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    # Relations
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission")

    # Contrainte d'unicité
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="unique_role_permission"),
    )


class AuditLog(Base):
    """Modèle pour l'historique des actions utilisateurs."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # create, update, delete, login, etc.
    resource = Column(String(50), nullable=False)  # users, books, roles, etc.
    resource_id = Column(String(50))  # ID de la ressource concernée
    details = Column(JSON, default=dict)  # Données supplémentaires
    ip_address = Column(String(45))  # Support IPv4 et IPv6
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog user={self.user_id} action={self.action} resource={self.resource}>"

    def to_dict(self) -> dict:
        """Convertit l'audit log en dictionnaire."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "details": self.details or {},
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class Library(Base):
    """Modèle de bibliothèque d'audiobooks."""

    __tablename__ = "libraries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    path = Column(String(255), nullable=False, unique=True)
    is_public = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    owner = relationship("User", back_populates="libraries")
    books = relationship("Book", back_populates="library", cascade="all, delete-orphan")


class Book(Base):
    """Modèle de livre audio."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255))
    authors = Column(JSON)  # Liste des auteurs
    narrators = Column(JSON)  # Liste des narrateurs
    series = Column(JSON)  # Informations sur la série
    description = Column(Text)
    publisher = Column(String(255))
    publish_year = Column(Integer)
    genres = Column(JSON)  # Liste des genres
    duration = Column(Integer)  # Durée en secondes
    size = Column(Integer)  # Taille en octets
    path = Column(String(255), nullable=False)
    cover_path = Column(String(255))
    isbn = Column(String(20))
    language = Column(String(10))
    explicit = Column(Boolean, default=False)
    abridged = Column(Boolean, default=False)
    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    library = relationship("Library", back_populates="books")
    owner = relationship("User", back_populates="books")
    tags = relationship("Tag", secondary=book_tags, back_populates="books")
    chapters = relationship(
        "Chapter", back_populates="book", cascade="all, delete-orphan"
    )


class Chapter(Base):
    """Modèle de chapitre de livre audio."""

    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    start_time = Column(Float, nullable=False)  # En secondes
    end_time = Column(Float, nullable=False)  # En secondes
    file_path = Column(String(255), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    # Relations
    book = relationship("Book", back_populates="chapters")


class Tag(Base):
    """Modèle d'étiquettes pour les livres audio."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    # Relations
    books = relationship("Book", secondary=book_tags, back_populates="tags")


# Modèles Pydantic pour la validation des données
class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: str = "fr"
    timezone: str = "Europe/Paris"
    metadata: Optional[dict] = None
    email_verified: bool = False
    two_factor_enabled: bool = False


class UserCreate(UserBase):
    model_config = ConfigDict(from_attributes=True)

    password: str

    # Explicitly include required fields from UserBase
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    metadata: Optional[dict] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime] = None
    login_attempts: Optional[int] = None
    locked_until: Optional[datetime] = None


class RoleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    name: str
    permission_ids: Optional[List[int]] = None


class RoleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleInDB(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PermissionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    codename: str
    description: Optional[str] = None
    resource: str
    action: str


class PermissionCreate(PermissionBase):
    model_config = ConfigDict(from_attributes=True)


class PermissionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    codename: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


class PermissionInDB(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AuditLogBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogInDB(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    timestamp: datetime


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str


class TokenData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: Optional[str] = None


class BookBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    subtitle: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    narrators: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    publisher: Optional[str] = None
    publish_year: Optional[int] = None
    genres: List[str] = Field(default_factory=list)
    isbn: Optional[str] = None
    language: str = "fr"
    explicit: bool = False
    abridged: bool = False


class BookCreate(BookBase):
    model_config = ConfigDict(from_attributes=True)

    library_id: int
    path: str


class BookInDB(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    duration: int
    size: int
    cover_path: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime


class LibraryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    path: str
    is_public: bool = False


class LibraryCreate(LibraryBase):
    model_config = ConfigDict(from_attributes=True)


class LibraryInDB(LibraryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
