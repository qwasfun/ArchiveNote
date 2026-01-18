import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.database import Base
from app.services.storage import get_public_url


class User(Base):
    __tablename__ = "users"
    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    username = Column(String)
    nickname = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class SystemAdmin(Base):
    """系统管理员表"""

    __tablename__ = "system_admins"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(
        String(36), ForeignKey("users.id"), nullable=True
    )  # 授予权限的管理员


# Workspace-User Many-to-Many Association Table
workspace_user_association = Table(
    "workspace_user_association",
    Base.metadata,
    Column(
        "workspace_id",
        String(36),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role", String, nullable=False, default="member"
    ),  # owner / admin / member / readonly
    Column("created_at", DateTime, default=datetime.utcnow),
)


class Workspace(Base):
    """Workspace - 配置隔离边界"""

    __tablename__ = "workspaces"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    files: Mapped[List["File"]] = relationship("File", back_populates="workspace")
    storage_backends: Mapped[List["StorageBackendConfig"]] = relationship(
        "StorageBackendConfig", back_populates="workspace"
    )


# Folder-Note Many-to-Many Association Table
folder_note_association = Table(
    "folder_note_association",
    Base.metadata,
    Column(
        "folder_id",
        String(36),
        ForeignKey("folders.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "note_id",
        String(36),
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Folder(Base):
    __tablename__ = "folders"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(String(36), ForeignKey("users.id"))  # 创建者
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("folders.id"), nullable=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(
        Integer, default=0
    )  # 0: False, 1: True. Using Integer for boolean behavior in some DBs or just standardizing
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    files = relationship("File", back_populates="folder")
    subfolders = relationship("Folder", backref=backref("parent", remote_side=[id]))
    notes: Mapped[List["Note"]] = relationship(
        secondary=folder_note_association, back_populates="folders", lazy="selectin"
    )

    @property
    def notes_count(self) -> int:
        return len(self.notes)


# Many-to-Many Association Table
file_note_association = Table(
    "file_note_association",
    Base.metadata,
    Column(
        "file_id",
        String(36),
        ForeignKey("files.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "note_id",
        String(36),
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class File(Base):
    __tablename__ = "files"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(String(36), ForeignKey("users.id"))  # 上传者
    folder_id = Column(String(36), ForeignKey("folders.id"), nullable=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    storage_backend_id = Column(
        String(36), ForeignKey("storage_backends.id"), nullable=True
    )
    filename: Mapped[str] = mapped_column(String, index=True)
    storage_path: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=0)
    file_type: Mapped[str] = mapped_column(
        String, nullable=True, index=True
    )  # text, document, image, video, binary
    file_type_confidence: Mapped[str] = mapped_column(
        String, nullable=True
    )  # high, medium, low
    original_created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    original_updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    folder = relationship("Folder", back_populates="files")
    workspace = relationship("Workspace", back_populates="files")

    # Relationship to Notes
    notes: Mapped[List["Note"]] = relationship(
        secondary=file_note_association, back_populates="files", lazy="selectin"
    )

    @property
    def notes_count(self) -> int:
        return len(self.notes)

    @property
    def download_url(self) -> str:
        return f"/api/v1/files/download/{self.id}/{self.filename}"

    @property
    def preview_url(self) -> str:
        return f"/api/v1/files/preview/{self.id}/{self.filename}"


class Note(Base):
    __tablename__ = "notes"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(String(36), ForeignKey("users.id"))  # 创建者
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # visibility: PRIVATE / PROTECTED / PUBLIC, default PRIVATE
    visibility = Column(String, default="PRIVATE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship to Files
    files: Mapped[List["File"]] = relationship(
        secondary=file_note_association, back_populates="notes", lazy="selectin"
    )
    # Relationship to Folders
    folders: Mapped[List["Folder"]] = relationship(
        secondary=folder_note_association, back_populates="notes", lazy="selectin"
    )


class StorageBackendConfig(Base):
    """存储后端配置"""

    __tablename__ = "storage_backends"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    backend_type: Mapped[str] = mapped_column(String, nullable=False)  # local or s3
    is_active: Mapped[bool] = mapped_column(Integer, default=0)  # 0: False, 1: True
    is_default: Mapped[bool] = mapped_column(Integer, default=0)  # 0: False, 1: True

    # 配置参数 (JSON格式存储)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)

    # 是否允许客户端直传 (仅对S3类型有效)
    allow_client_direct_upload: Mapped[bool] = mapped_column(
        Integer, default=0
    )  # 0: False, 1: True

    # 元数据
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # Relationship
    workspace = relationship("Workspace", back_populates="storage_backends")
