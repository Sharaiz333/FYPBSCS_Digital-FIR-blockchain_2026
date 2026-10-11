from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import RoleName


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=128)
    role: RoleName


class UserUpdate(BaseModel):
    # Every field optional: PATCH only changes what is sent.
    # Password changes are deliberately NOT here; they get their own endpoint later.
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    role: RoleName | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    # No password_hash here, so it can never leak through the API.
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    full_name: str
    username: str
    email: str | None
    role: RoleName
    is_active: bool
    created_at: datetime