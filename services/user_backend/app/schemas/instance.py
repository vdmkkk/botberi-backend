from pydantic import BaseModel, Field

from shared_psql_models.models import KBDataType, KBLangHint
from shared_psql_models.schemas import (
    InstanceSchema,
    KnowledgeBaseEntrySchema,
    KnowledgeBaseSchema,
)


class InstanceCreate(BaseModel):
    bot_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    user_config: dict = Field(default_factory=dict)
    pipeline_config: dict = Field(default_factory=dict)


class InstanceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    user_config: dict | None = None
    pipeline_config: dict | None = None


class KnowledgeBaseEntryCreate(BaseModel):
    content: str = Field(min_length=1)
    data_type: KBDataType | None = None
    lang_hint: KBLangHint | None = None


InstanceOut = InstanceSchema
KnowledgeBaseOut = KnowledgeBaseSchema
KnowledgeBaseEntryOut = KnowledgeBaseEntrySchema

__all__ = [
    "InstanceCreate",
    "InstanceUpdate",
    "InstanceOut",
    "KnowledgeBaseOut",
    "KnowledgeBaseEntryCreate",
    "KnowledgeBaseEntryOut",
]


