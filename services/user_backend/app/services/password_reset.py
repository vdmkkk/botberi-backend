import secrets

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.crud import users as user_crud
from app.services import cache

settings = get_settings()


def _token_key(token: str) -> str:
    return f"password-reset:{token}"


async def create_reset_slug(db: AsyncSession, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    await cache.cache_set(_token_key(token), {"user_id": user_id}, settings.password_reset_ttl_seconds)
    return token


async def consume_reset_slug(db: AsyncSession, token: str, new_password: str) -> None:
    cached = await cache.cache_get(_token_key(token))
    if cached is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reset link expired or invalid")
    user = await user_crud.get_user_by_id(db, cached["user_id"])
    if user is None:
        await cache.cache_delete(_token_key(token))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await user_crud.update_password(db, user, hash_password(new_password))
    await cache.cache_delete(_token_key(token))


__all__ = ["create_reset_slug", "consume_reset_slug"]


