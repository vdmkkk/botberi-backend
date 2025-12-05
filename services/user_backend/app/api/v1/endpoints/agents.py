from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_shared_db
from shared_psql_models.models import Agent
from shared_psql_models.schemas import AgentSchema

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentSchema])
async def list_agents(db: AsyncSession = Depends(get_shared_db)) -> list[AgentSchema]:
    result = await db.execute(select(Agent).order_by(Agent.id))
    agents = result.scalars().all()
    return [AgentSchema.model_validate(agent) for agent in agents]


@router.get("/{agent_id}", response_model=AgentSchema)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_shared_db)) -> AgentSchema:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentSchema.model_validate(agent)


__all__ = ["router"]


