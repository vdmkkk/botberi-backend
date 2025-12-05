from uuid import UUID

from pydantic import BaseModel

from shared_psql_models.models.instance import InstanceStatus


class InstanceSchema(BaseModel):
    """Pydantic representation shared across services."""

    id: UUID
    agent_id: UUID
    user_id: UUID
    status: InstanceStatus
    config: dict
    metadata: dict | None = None
    last_error: str | None = None
    display_name: str | None = None

    class Config:
        from_attributes = True


__all__ = ["InstanceSchema"]


