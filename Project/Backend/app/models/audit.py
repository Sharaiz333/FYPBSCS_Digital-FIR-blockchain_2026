import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    """Off-chain record of every workflow action: who, what, when, and the
    status before/after (FR-13). Rows are only ever added, never edited.
    'detail' must never contain personal data such as a CNIC."""

    __tablename__ = "audit_logs"

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    entity_type: str = Field(index=True)  # "complaint" or "fir"
    entity_id: str = Field(index=True)
    action: str
    from_status: str | None = None
    to_status: str | None = None
    actor_id: str = Field(foreign_key="users.user_id")
    actor_role: str
    detail: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)