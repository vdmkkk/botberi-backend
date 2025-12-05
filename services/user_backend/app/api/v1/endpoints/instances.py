from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.api.deps import get_current_user, get_shared_db
from app.models.user import User
from app.schemas import (
    InstanceCreate,
    InstanceOut,
    InstanceUpdate,
    KnowledgeBaseEntryCreate,
    KnowledgeBaseEntryOut,
)
from app.services.event_bus import emit_event
from shared_psql_models.models import (
    Agent,
    Instance,
    KnowledgeBase,
    KnowledgeBaseEntry,
)

router = APIRouter(prefix="/instances", tags=["instances"])


@router.post("", response_model=InstanceOut, status_code=status.HTTP_201_CREATED)
async def create_instance(
    payload: InstanceCreate,
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> InstanceOut:
    agent = await shared_db.get(Agent, payload.bot_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    instance = Instance(
        bot_id=payload.bot_id,
        user_id=current_user.id,
        title=payload.title,
        user_config=payload.user_config,
        pipeline_config=payload.pipeline_config,
    )
    shared_db.add(instance)
    await shared_db.flush()

    knowledge_base = KnowledgeBase(instance=instance)
    shared_db.add(knowledge_base)
    await shared_db.commit()
    await shared_db.refresh(instance)
    await shared_db.refresh(knowledge_base)

    await emit_event(
        "instance.created",
        {
            "instance_id": instance.id,
            "bot_id": instance.bot_id,
            "user_id": current_user.id,
        },
    )
    await emit_event(
        "knowledge_base.created",
        {
            "knowledge_base_id": knowledge_base.id,
            "instance_id": instance.id,
        },
    )
    instance.knowledge_base = knowledge_base
    return InstanceOut.model_validate(instance)


@router.get("", response_model=list[InstanceOut])
async def list_instances(
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> list[InstanceOut]:
    stmt = (
        select(Instance)
        .options(
            selectinload(Instance.knowledge_base).selectinload(KnowledgeBase.entries),
        )
        .where(Instance.user_id == current_user.id)
        .order_by(Instance.id)
    )
    result = await shared_db.execute(stmt)
    instances = result.scalars().unique().all()
    return [InstanceOut.model_validate(instance) for instance in instances]


@router.get("/{instance_id}", response_model=InstanceOut)
async def get_instance(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> InstanceOut:
    instance = await _get_instance(shared_db, current_user.id, instance_id)
    return InstanceOut.model_validate(instance)


@router.patch("/{instance_id}", response_model=InstanceOut)
async def update_instance(
    instance_id: int,
    payload: InstanceUpdate,
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> InstanceOut:
    instance = await _get_instance(shared_db, current_user.id, instance_id)

    if payload.title is not None:
        instance.title = payload.title
    if payload.user_config is not None:
        instance.user_config = payload.user_config
    if payload.pipeline_config is not None:
        instance.pipeline_config = payload.pipeline_config

    await shared_db.commit()
    await shared_db.refresh(instance)
    await emit_event(
        "instance.updated",
        {"instance_id": instance.id, "user_id": current_user.id},
    )
    return InstanceOut.model_validate(instance)


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> None:
    instance = await _get_instance(shared_db, current_user.id, instance_id, load_relations=False)
    await shared_db.delete(instance)
    await shared_db.commit()
    await emit_event("instance.deleted", {"instance_id": instance_id, "user_id": current_user.id})


@router.post("/{instance_id}/knowledge-base/entries", response_model=KnowledgeBaseEntryOut, status_code=status.HTTP_201_CREATED)
async def add_knowledge_base_entry(
    instance_id: int,
    payload: KnowledgeBaseEntryCreate,
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> KnowledgeBaseEntryOut:
    instance = await _get_instance(shared_db, current_user.id, instance_id)
    if not instance.knowledge_base:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Knowledge base missing")
    entry = KnowledgeBaseEntry(
        knowledge_base_id=instance.knowledge_base.id,
        content=payload.content,
        data_type=payload.data_type,
        lang_hint=payload.lang_hint,
    )
    shared_db.add(entry)
    await shared_db.commit()
    await shared_db.refresh(entry)
    await emit_event(
        "knowledge_base.entry.created",
        {
            "knowledge_base_id": instance.knowledge_base.id,
            "entry_id": entry.id,
            "instance_id": instance.id,
        },
    )
    return KnowledgeBaseEntryOut.model_validate(entry)


@router.get("/{instance_id}/knowledge-base/entries", response_model=list[KnowledgeBaseEntryOut])
async def list_knowledge_base_entries(
    instance_id: int,
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> list[KnowledgeBaseEntryOut]:
    instance = await _get_instance(shared_db, current_user.id, instance_id)
    if not instance.knowledge_base:
        return []
    stmt = (
        select(KnowledgeBaseEntry)
        .where(KnowledgeBaseEntry.knowledge_base_id == instance.knowledge_base.id)
        .order_by(KnowledgeBaseEntry.id)
    )
    result = await shared_db.execute(stmt)
    entries = result.scalars().all()
    return [KnowledgeBaseEntryOut.model_validate(entry) for entry in entries]


@router.delete("/{instance_id}/knowledge-base/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base_entry(
    instance_id: int,
    entry_id: int,
    current_user: User = Depends(get_current_user),
    shared_db: AsyncSession = Depends(get_shared_db),
) -> None:
    instance = await _get_instance(shared_db, current_user.id, instance_id)
    if not instance.knowledge_base:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")
    stmt = select(KnowledgeBaseEntry).where(
        KnowledgeBaseEntry.id == entry_id,
        KnowledgeBaseEntry.knowledge_base_id == instance.knowledge_base.id,
    )
    result = await shared_db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    await shared_db.delete(entry)
    await shared_db.commit()
    await emit_event(
        "knowledge_base.entry.deleted",
        {
            "knowledge_base_id": instance.knowledge_base.id,
            "entry_id": entry_id,
            "instance_id": instance.id,
        },
    )


async def _get_instance(
    shared_db: AsyncSession,
    user_id: int,
    instance_id: int,
    load_relations: bool = True,
) -> Instance:
    stmt = select(Instance).where(
        Instance.id == instance_id,
        Instance.user_id == user_id,
    )
    if load_relations:
        stmt = stmt.options(
            joinedload(Instance.knowledge_base).selectinload(KnowledgeBase.entries)
        )
    result = await shared_db.execute(stmt)
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return instance


__all__ = ["router"]


