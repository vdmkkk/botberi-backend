from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared_psql_models.base import Base, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover - import-time only
    from .agent import Agent


class InstanceStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    DELETED = "deleted"


class Instance(TimestampMixin, Base):
    """Canonical definition of per-user agent instances."""

    __tablename__ = "agent_instances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[InstanceStatus] = mapped_column(
        Enum(InstanceStatus, name="instance_status"),
        nullable=False,
        default=InstanceStatus.PENDING,
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)

    agent: Mapped["Agent"] = relationship(back_populates="instances")


__all__ = ["Instance", "InstanceStatus"]


