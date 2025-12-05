from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, constr


class UserProfile(BaseModel):
    id: int
    name: str
    company: str
    email: EmailStr
    phone: str | None = None
    telegram: str | None = None
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True


class RegistrationRequest(BaseModel):
    name: constr(min_length=1, max_length=120)
    company: constr(min_length=1, max_length=120)
    email: EmailStr
    password: constr(min_length=8, max_length=128)
    phone: constr(min_length=6, max_length=64) | None = None
    telegram: constr(min_length=3, max_length=64) | None = None


class RegistrationConfirm(BaseModel):
    email: EmailStr
    code: constr(min_length=6, max_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class ProfileUpdate(BaseModel):
    name: constr(min_length=1, max_length=120)
    company: constr(min_length=1, max_length=120)
    phone: constr(min_length=6, max_length=64) | None = None
    telegram: constr(min_length=3, max_length=64) | None = None


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=10, max_length=256)
    new_password: constr(min_length=8, max_length=128)


