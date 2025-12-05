from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared_psql_models.base import Base, JSONBCompat, TimestampMixin


class InstanceStatus(str, enum.Enum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


class KBEntryStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class KBDataType(str, enum.Enum):
    DOCUMENT = "document"
    VIDEO = "video"
    OTHER = "other"


class KBLangHint(str, enum.Enum):
    EN = "en"
    ES = "es"
    OTHER = "other"


class Instance(TimestampMixin, Base):
    """Canonical definition of user-created bot instances."""

    __tablename__ = "instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bot_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    user_config: Mapped[dict] = mapped_column(JSONBCompat, nullable=False, default=dict)
    pipeline_config: Mapped[dict] = mapped_column(JSONBCompat, nullable=False, default=dict)
    status: Mapped[InstanceStatus] = mapped_column(
        Enum(InstanceStatus, name="instance_status"),
        nullable=False,
        default=InstanceStatus.PENDING,
    )

    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        back_populates="instance",
        cascade="all, delete-orphan",
        uselist=False,
    )


class KnowledgeBase(TimestampMixin, Base):
    """One-to-one knowledge base container per instance."""

    __tablename__ = "knowledge_bases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instance_id: Mapped[int] = mapped_column(
        ForeignKey("instances.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    instance: Mapped[Instance] = relationship(back_populates="knowledge_base")
    entries: Mapped[list["KnowledgeBaseEntry"]] = relationship(
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )


class KnowledgeBaseEntry(TimestampMixin, Base):
    """Individual knowledge base entries tied to an instance."""

    __tablename__ = "knowledge_base_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    knowledge_base_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    data_type: Mapped[KBDataType | None] = mapped_column(
        Enum(KBDataType, name="kb_data_type"),
        nullable=True,
    )
    lang_hint: Mapped[KBLangHint | None] = mapped_column(
        Enum(KBLangHint, name="kb_lang_hint"),
        nullable=True,
    )
    status: Mapped[KBEntryStatus] = mapped_column(
        Enum(KBEntryStatus, name="kb_entry_status"),
        nullable=False,
        default=KBEntryStatus.QUEUED,
    )

    knowledge_base: Mapped[KnowledgeBase] = relationship(back_populates="entries")


__all__ = [
    "Instance",
    "InstanceStatus",
    "KnowledgeBase",
    "KnowledgeBaseEntry",
    "KBEntryStatus",
    "KBDataType",
    "KBLangHint",
]

