from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.crud import users as user_crud
from app.models.user import User
from app.schemas import (
    AuthResponse,
    LoginRequest,
    PasswordResetConfirm,
    RegistrationConfirm,
    RegistrationRequest,
    UserProfile,
)
from app.services.notifications import (
    queue_password_reset_email,
    queue_verification_email,
)
from app.services.password_reset import consume_reset_slug, create_reset_slug
from app.services.registration import confirm_registration, start_registration

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register/request", status_code=status.HTTP_202_ACCEPTED)
async def request_registration(
    payload: RegistrationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    code = await start_registration(db, payload)
    queue_verification_email(background_tasks, payload.email, code)
    return {"message": "Verification code sent"}


@router.post("/register/confirm", status_code=status.HTTP_201_CREATED)
async def confirm_registration_endpoint(
    payload: RegistrationConfirm,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await confirm_registration(db, payload.email, payload.code)
    return {"message": "Account activated"}


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    user = await user_crud.get_user_by_email(db, payload.email.lower())
    if not user or not verify_password(payload.password, user.hashed_password):
        raise_invalid_credentials()

    token = issue_token(response, user)
    return AuthResponse(access_token=token, user=UserProfile.model_validate(user))


@router.post("/password/reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    token = await create_reset_slug(db, current_user.id)
    link = settings.password_reset_url_template.format(token=token)
    queue_password_reset_email(background_tasks, current_user.email, link)
    return {"message": "Password reset link sent"}


@router.post("/password/reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await consume_reset_slug(db, payload.token, payload.new_password)
    return {"message": "Password updated"}


def issue_token(response: Response, user: User) -> str:
    token = create_access_token(str(user.id), {"email": user.email})
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        max_age=settings.jwt_access_ttl_seconds,
        samesite="lax",
    )
    response.headers["X-Auth-Token"] = token
    return token


def raise_invalid_credentials() -> None:
    from fastapi import HTTPException

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


__all__ = [
    "router",
]


