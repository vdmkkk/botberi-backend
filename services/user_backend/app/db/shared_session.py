from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

_shared_engine: AsyncEngine | None = None
_shared_session_factory: async_sessionmaker | None = None


def get_shared_engine() -> AsyncEngine:
    global _shared_engine
    if _shared_engine is None:
        if not settings.shared_pg_dsn:
            raise RuntimeError("SHARED_PG_DSN is not configured")
        _shared_engine = create_async_engine(settings.shared_pg_dsn, future=True)
    return _shared_engine


def get_shared_session_factory() -> async_sessionmaker:
    global _shared_session_factory
    if _shared_session_factory is None:
        engine = get_shared_engine()
        _shared_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    return _shared_session_factory


async def get_shared_session() -> AsyncGenerator:
    session_factory = get_shared_session_factory()
    async with session_factory() as session:
        yield session


__all__ = ["get_shared_session", "get_shared_engine", "get_shared_session_factory"]


