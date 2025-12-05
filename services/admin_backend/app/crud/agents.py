from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared_psql_models.models import Agent


async def list_agents(db: AsyncSession) -> list[Agent]:
    result = await db.execute(select(Agent).order_by(Agent.id))
    return list(result.scalars().all())


async def get_agent(db: AsyncSession, agent_id: int) -> Agent | None:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    return result.scalar_one_or_none()


async def create_agent(
    db: AsyncSession,
    *,
    title: str,
    content: dict,
    activation_code: str,
    rate: int,
) -> Agent:
    agent = Agent(
        title=title,
        content=content,
        activation_code=activation_code,
        rate=rate,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def update_agent(
    db: AsyncSession,
    agent: Agent,
    *,
    title: str | None = None,
    content: dict | None = None,
    activation_code: str | None = None,
    rate: int | None = None,
) -> Agent:
    if title is not None:
        agent.title = title
    if content is not None:
        agent.content = content
    if activation_code is not None:
        agent.activation_code = activation_code
    if rate is not None:
        agent.rate = rate

    await db.commit()
    await db.refresh(agent)
    return agent


async def delete_agent(db: AsyncSession, agent: Agent) -> None:
    await db.delete(agent)
    await db.commit()


__all__ = [
    "list_agents",
    "get_agent",
    "create_agent",
    "update_agent",
    "delete_agent",
]


