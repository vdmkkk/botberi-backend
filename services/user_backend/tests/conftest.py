import asyncio
import json
from collections.abc import AsyncGenerator

import fakeredis.aioredis
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.config import get_settings
from app.db.base import Base
from app.main import app
from app.services import cache as cache_module

SQLITE_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLITE_TEST_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def configure_settings() -> None:
    settings = get_settings()
    settings.environment = "test"
    settings.jwt_secret = "test-secret"
    settings.redis_url = "redis://test"


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
async def client(db_session: AsyncSession, fake_redis) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

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


