import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return _redis_client


async def cache_set(key: str, value: dict[str, Any], ttl_seconds: int) -> None:
    client = get_redis_client()
    await client.set(key, json.dumps(value), ex=ttl_seconds)


async def cache_get(key: str) -> dict[str, Any] | None:
    client = get_redis_client()
    raw = await client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def cache_delete(key: str) -> None:
    client = get_redis_client()
    await client.delete(key)


async def cache_exists(key: str) -> bool:
    client = get_redis_client()
    return bool(await client.exists(key))


__all__ = ["get_redis_client", "cache_set", "cache_get", "cache_delete", "cache_exists"]


