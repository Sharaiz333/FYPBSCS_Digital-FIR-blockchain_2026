from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    entity_type: str
    entity_id: str
    action: str
    from_status: str | None
    to_status: str | None
    actor_id: str
    actor_role: str
    detail: str | None
    created_at: datetime