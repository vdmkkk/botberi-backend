from uuid import UUID

from pydantic import BaseModel, Field

from shared_psql_models.models.agent import AgentLifecycle


class AgentSchema(BaseModel):
    """Pydantic representation shared across services."""

    id: UUID
    name: str
    slug: str
    version: str = Field(default="v1")
    status: AgentLifecycle
    description: str | None = None
    config_schema: dict
    owner_team: str | None = None

    class Config:
        from_attributes = True


__all__ = ["AgentSchema"]


