from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserRead(UserBase):
    id: UUID
    created_at: datetime


class UserCreate(UserBase):
    password: str


