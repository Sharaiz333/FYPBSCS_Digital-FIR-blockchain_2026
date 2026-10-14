from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import VerificationStatus


class PendingCitizenRead(BaseModel):
    """What a verifying officer sees. Includes the full CNIC because the
    officer must compare it with the citizen's original card. This schema
    is only ever returned by officer-only endpoints."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    full_name: str
    username: str
    email: str | None
    cnic: str | None
    phone: str | None
    address: str | None
    verification_status: VerificationStatus
    created_at: datetime
    verified_at: datetime | None
    rejection_reason: str | None


class VerificationDecision(BaseModel):
    approve: bool
    reason: str | None = Field(default=None, max_length=300)