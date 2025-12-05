from pydantic import BaseModel

from shared_psql_models.models.instance import (
    InstanceStatus,
    KBDataType,
    KBEntryStatus,
    KBLangHint,
)


class KnowledgeBaseEntrySchema(BaseModel):
    id: int
    knowledge_base_id: int
    content: str
    data_type: KBDataType | None = None
    lang_hint: KBLangHint | None = None
    status: KBEntryStatus

    class Config:
        from_attributes = True


class KnowledgeBaseSchema(BaseModel):
    id: int
    instance_id: int
    entries: list[KnowledgeBaseEntrySchema] = []

    class Config:
        from_attributes = True


class InstanceSchema(BaseModel):
    id: int
    bot_id: int
    user_id: int
    title: str
    user_config: dict
    pipeline_config: dict
    status: InstanceStatus
    knowledge_base: KnowledgeBaseSchema | None = None

    class Config:
        from_attributes = True


__all__ = ["InstanceSchema", "KnowledgeBaseSchema", "KnowledgeBaseEntrySchema"]


