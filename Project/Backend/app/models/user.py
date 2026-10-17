
import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel
from sqlalchemy import Enum as SAEnum

from app.models.enums import RoleName, VerificationStatus


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    full_name: str
    username: str = Field(index=True, unique=True)
    email: str | None = Field(default=None, index=True, unique=True)
    password_hash: str
    role: RoleName = Field(index=True)
    is_active: bool = Field(default=True)

    # Citizen registration details
    cnic: str | None = Field(default=None, index=True, unique=True)
    phone: str | None = None
    address: str | None = None

    # Verification status
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.NOT_REQUIRED,
        index=True,
        sa_type=SAEnum(
            VerificationStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="verificationstatus",
        ),
    )

    verified_by: str | None = Field(default=None, foreign_key="users.user_id")
    verified_at: datetime | None = None
    rejection_reason: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
