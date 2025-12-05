from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud import users as user_crud
from app.models.user import User
from app.schemas import ProfileUpdate, UserProfile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def read_profile(current_user: User = Depends(get_current_user)) -> UserProfile:
    return UserProfile.model_validate(current_user)


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    updated = await user_crud.update_profile(
        db,
        current_user,
        name=payload.name,
        company=payload.company,
        phone=payload.phone,
        telegram=payload.telegram,
    )
    return UserProfile.model_validate(updated)


__all__ = ["router"]


