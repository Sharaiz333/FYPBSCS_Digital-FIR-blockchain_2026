from sqlmodel import Session

from app.models.audit import AuditLog
from app.models.user import User


def log_event(
    session: Session,
    *,
    entity_type: str,
    entity_id: str,
    action: str,
    actor: User,
    from_status: str | None = None,
    to_status: str | None = None,
    detail: str | None = None,
) -> None:
    """Adds an audit row to the CURRENT transaction but does not commit.
    The caller commits once, so the business change and its audit entry
    are saved together or not at all."""
    session.add(
        AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor.user_id,
            actor_role=actor.role.value,
            from_status=from_status,
            to_status=to_status,
            detail=detail,
        )
    )