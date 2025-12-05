import secrets
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.crud import users as user_crud
from app.schemas.user import RegistrationRequest
from app.services import cache

settings = get_settings()


@dataclass
class RegistrationPayload:
    name: str
    company: str
    email: str
    hashed_password: str
    phone: str | None
    telegram: str | None


def _pending_key(email: str) -> str:
    return f"registration:pending:{email.lower()}"


def _throttle_key(email: str) -> str:
    return f"registration:cooldown:{email.lower()}"


async def start_registration(db: AsyncSession, payload: RegistrationRequest) -> str:
    email = payload.email.lower()
    existing = await user_crud.get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if await cache.cache_exists(_throttle_key(email)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before requesting another code",
        )

    code = f"{secrets.randbelow(1_000_000):06d}"
    registration_payload = RegistrationPayload(
        name=payload.name,
        company=payload.company,
        email=email,
        hashed_password=hash_password(payload.password),
        phone=payload.phone,
        telegram=payload.telegram,
    )
    await cache.cache_set(
        _pending_key(email),
        registration_payload.__dict__ | {"code": code},
        settings.registration_code_ttl_seconds,
    )
    await cache.cache_set(_throttle_key(email), {"value": True}, settings.registration_code_cooldown_seconds)
    return code


async def confirm_registration(db: AsyncSession, email: str, code: str) -> None:
    email_normalized = email.lower()
    cached = await cache.cache_get(_pending_key(email_normalized))
    if cached is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pending registration found")
    if cached.get("code") != code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    await user_crud.create_user(
        db,
        name=cached["name"],
        company=cached["company"],
        email=email_normalized,
        hashed_password=cached["hashed_password"],
        phone=cached.get("phone"),
        telegram=cached.get("telegram"),
    )
    await cache.cache_delete(_pending_key(email_normalized))
    await cache.cache_delete(_throttle_key(email_normalized))


__all__ = ["start_registration", "confirm_registration"]


