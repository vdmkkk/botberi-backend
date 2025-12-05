import asyncio
import json
from collections.abc import AsyncGenerator

import fakeredis.aioredis
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db, get_shared_db
from app.core.config import get_settings
from app.db.base import Base
from app.main import app
from app.services import cache as cache_module
from shared_psql_models import Base as SharedBase
from shared_psql_models.models import Agent

SQLITE_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
SHARED_SQLITE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLITE_TEST_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
shared_engine = create_async_engine(SHARED_SQLITE_URL, future=True)
SharedTestingSession = async_sessionmaker(bind=shared_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with shared_engine.begin() as conn:
        await conn.run_sync(SharedBase.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with shared_engine.begin() as conn:
        await conn.run_sync(SharedBase.metadata.drop_all)


@pytest.fixture(autouse=True)
def configure_settings() -> None:
    settings = get_settings()
    settings.environment = "test"
    settings.jwt_secret = "test-secret"
    settings.redis_url = "redis://test"
    settings.event_emit_enabled = False
    settings.shared_pg_dsn = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def fake_redis():
    client = fakeredis.aioredis.FakeRedis(encoding="utf-8", decode_responses=True)
    cache_module._redis_client = client
    yield client
    await client.flushall()
    await client.close()
    cache_module._redis_client = None


@pytest.fixture
async def shared_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SharedTestingSession() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession, shared_db_session: AsyncSession, fake_redis) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield db_session

    async def _override_get_shared_db():
        yield shared_db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_shared_db] = _override_get_shared_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def registered_user(client: AsyncClient, fake_redis) -> dict:
    payload = {
        "name": "Test User",
        "company": "Botberi",
        "email": "test@example.com",
        "password": "secret123",
        "phone": "+1000000000",
        "telegram": "@testuser",
    }
    await client.post("/api/v1/auth/register/request", json=payload)
    cached = await fake_redis.get("registration:pending:test@example.com")
    code = json.loads(cached)["code"]
    await client.post("/api/v1/auth/register/confirm", json={"email": payload["email"], "code": code})
    return payload


@pytest.fixture
async def seeded_agents(shared_db_session: AsyncSession) -> list[Agent]:
    agents = [
        Agent(title="Agent A", content={"desc": "A"}, activation_code="A1", rate=10),
        Agent(title="Agent B", content={"desc": "B"}, activation_code="B1", rate=5),
    ]
    shared_db_session.add_all(agents)
    await shared_db_session.commit()
    for agent in agents:
        await shared_db_session.refresh(agent)
    return agents


