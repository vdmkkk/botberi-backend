from pydantic import BaseModel, Field


class AgentSchema(BaseModel):
    """Pydantic representation shared across services."""

    id: int
    title: str = Field(max_length=200)
    content: dict
    activation_code: str
    rate: int

    class Config:
        from_attributes = True


__all__ = ["AgentSchema"]


