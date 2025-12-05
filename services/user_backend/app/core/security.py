from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> str:
    payload: Dict[str, Any] = {"sub": subject}
    if extra_claims:
        payload.update(extra_claims)
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.jwt_access_ttl_seconds)
    payload["exp"] = expire
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except JWTError as exc:  # pragma: no cover - jose error messages vary
        raise ValueError("Invalid authentication token") from exc


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
]


