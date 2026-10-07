import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.models.enums import RoleName


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    full_name: str
    username: str = Field(index=True, unique=True)
    email: str | None = Field(default=None, index=True, unique=True)
    password_hash: str
    role: RoleName = Field(index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))