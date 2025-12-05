from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import get_settings


settings = get_settings()


def build_async_engine() -> AsyncEngine:
    return create_async_engine(settings.database_url, future=True, echo=settings.environment == "development")


engine = build_async_engine()
async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

__all__ = ["engine", "async_session_factory", "build_async_engine"]


