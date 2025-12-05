from pydantic import BaseModel, Field

from shared_psql_models.schemas import AgentSchema


class AgentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: dict
    activation_code: str = Field(min_length=3, max_length=64)
    rate: int = Field(ge=0)


class AgentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: dict | None = None
    activation_code: str | None = Field(None, min_length=3, max_length=64)
    rate: int | None = Field(None, ge=0)


AgentOut = AgentSchema

__all__ = ["AgentCreate", "AgentUpdate", "AgentOut"]


