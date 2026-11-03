from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def commit_or_conflict(session: Session) -> None:
    """Commit; turn a database uniqueness clash (two people doing the same thing
    at the same instant, e.g. two FIR numbers colliding) into a clean 409."""
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Another change happened at the same time. Please try again.",
        )