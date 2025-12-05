from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    name: str,
    company: str,
    email: str,
    hashed_password: str,
    phone: str | None,
    telegram: str | None,
) -> User:
    user = User(
        name=name,
        company=company,
        email=email,
        hashed_password=hashed_password,
        phone=phone,
        telegram=telegram,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_profile(
    db: AsyncSession,
    user: User,
    *,
    name: str,
    company: str,
    phone: str | None,
    telegram: str | None,
) -> User:
    user.name = name
    user.company = company
    user.phone = phone
    user.telegram = telegram
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(db: AsyncSession, user: User, hashed_password: str) -> None:
    user.hashed_password = hashed_password
    await db.commit()


__all__ = [
    "get_user_by_email",
    "get_user_by_id",
    "create_user",
    "update_profile",
    "update_password",
]


