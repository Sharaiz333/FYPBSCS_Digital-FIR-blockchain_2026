from typing import Literal

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import require_role
from app.models.audit import AuditLog
from app.models.enums import RoleName
from app.models.user import User
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/{entity_type}/{entity_id}", response_model=list[AuditLogRead])
def get_audit_trail(
    entity_type: Literal["complaint", "fir"],
    entity_id: str,
    session: Session = Depends(get_session),
    _user: User = Depends(
        require_role(RoleName.SUPERVISORY_OFFICER, RoleName.AUDIT_REVIEW_OFFICER, RoleName.ADMIN)
    ),
):
    """Oldest first. Read-only: there is intentionally no endpoint that edits or deletes audit rows."""
    statement = (
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.created_at)
    )
    return session.exec(statement).all()