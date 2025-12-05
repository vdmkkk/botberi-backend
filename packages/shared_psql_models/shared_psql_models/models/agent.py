from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared_psql_models.base import Base, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover - import-time only
    from .instance import Instance


class AgentLifecycle(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    RETIRED = "retired"


class Agent(TimestampMixin, Base):
    """Canonical definition of the agents catalog rows."""

    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="v1")
    status: Mapped[AgentLifecycle] = mapped_column(
        Enum(AgentLifecycle, name="agent_lifecycle"),
        nullable=False,
        default=AgentLifecycle.DRAFT,
    )
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    config_schema: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    owner_team: Mapped[str | None] = mapped_column(String(120), nullable=True)

    instances: Mapped[list["Instance"]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


__all__ = ["Agent", "AgentLifecycle"]


