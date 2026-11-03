from datetime import datetime, timezone

from sqlmodel import Session, func, select


def next_reference(session: Session, column, prefix: str) -> str:
    """Next number like CMP-2026-000007 (prefix, year, 6-digit counter).

    Takes the highest existing number for this year and adds one. If two
    requests ever pick the same number at the same instant, the UNIQUE
    constraint on the column rejects the second one and the caller turns
    that into a 409 'please try again' (see common.commit_or_conflict)."""
    stem = f"{prefix}-{datetime.now(timezone.utc).year}-"
    highest = session.exec(select(func.max(column)).where(column.like(f"{stem}%"))).one()
    next_number = int(highest.rsplit("-", 1)[1]) + 1 if highest else 1
    return f"{stem}{next_number:06d}"