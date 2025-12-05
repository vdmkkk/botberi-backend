from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud import agents as agents_crud
from app.schemas import AgentCreate, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentOut])
async def list_agents(db: AsyncSession = Depends(get_db)) -> list[AgentOut]:
    agents = await agents_crud.list_agents(db)
    return [AgentOut.model_validate(agent) for agent in agents]


@router.post("", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(payload: AgentCreate, db: AsyncSession = Depends(get_db)) -> AgentOut:
    agent = await agents_crud.create_agent(
        db,
        title=payload.title,
        content=payload.content,
        activation_code=payload.activation_code,
        rate=payload.rate,
    )
    return AgentOut.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)) -> AgentOut:
    agent = await agents_crud.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentOut.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(agent_id: int, payload: AgentUpdate, db: AsyncSession = Depends(get_db)) -> AgentOut:
    agent = await agents_crud.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    updated = await agents_crud.update_agent(
        db,
        agent,
        title=payload.title,
        content=payload.content,
        activation_code=payload.activation_code,
        rate=payload.rate,
    )
    return AgentOut.model_validate(updated)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)) -> None:
    agent = await agents_crud.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    await agents_crud.delete_agent(db, agent)


__all__ = ["router"]


