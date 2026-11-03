from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.complaint import Complaint
from app.models.enums import FIR_TRANSITIONS, FIRStatus, RoleName
from app.models.fir import FIR
from app.models.user import User
from app.schemas.fir import ComplainantInfo, FIRRead
from app.services.audit_service import log_event
from app.services.common import commit_or_conflict, utcnow


def _can_view(viewer: User, fir: FIR, complaint: Complaint) -> bool:
    if viewer.role in (RoleName.POLICE_OFFICER, RoleName.SUPERVISORY_OFFICER, RoleName.AUDIT_REVIEW_OFFICER):
        return True
    if viewer.role == RoleName.INVESTIGATING_OFFICER:
        return fir.assigned_io == viewer.user_id
    if viewer.role == RoleName.CITIZEN:
        return complaint.complainant_user_id == viewer.user_id
    return False  # e.g. admin: manages users, not case content


def get_fir_for_viewer(session: Session, fir_id: str, viewer: User) -> tuple[FIR, Complaint]:
    fir = session.get(FIR, fir_id)
    complaint = session.get(Complaint, fir.complaint_id) if fir else None
    if not fir or not complaint or not _can_view(viewer, fir, complaint):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "FIR not found")
    return fir, complaint


def build_fir_reads(session: Session, firs: list[FIR]) -> list[FIRRead]:
    """List view: no personal data about the complainant."""
    complaint_ids = [f.complaint_id for f in firs]
    io_ids = [f.assigned_io for f in firs if f.assigned_io]
    complaints = session.exec(select(Complaint).where(Complaint.complaint_id.in_(complaint_ids))).all() if firs else []
    ios = session.exec(select(User).where(User.user_id.in_(io_ids))).all() if io_ids else []
    ref_by_id = {c.complaint_id: c.reference_number for c in complaints}
    name_by_id = {u.user_id: u.full_name for u in ios}

    reads = []
    for fir in firs:
        read = FIRRead.model_validate(fir)
        read.complaint_reference = ref_by_id.get(fir.complaint_id)
        read.assigned_io_name = name_by_id.get(fir.assigned_io) if fir.assigned_io else None
        reads.append(read)
    return reads


def build_fir_detail(session: Session, fir: FIR, complaint: Complaint, viewer: User) -> FIRRead:
    read = build_fir_reads(session, [fir])[0]
    # Data minimisation: the Audit/Review Officer checks integrity and history,
    # so they never need the complainant's personal details.
    if viewer.role != RoleName.AUDIT_REVIEW_OFFICER:
        read.complainant = ComplainantInfo(
            name=complaint.complainant_name,
            cnic=complaint.complainant_cnic,
            phone=complaint.complainant_phone,
            address=complaint.complainant_address,
        )
    return read


def list_firs(
    session: Session,
    viewer: User,
    *,
    status_filter: FIRStatus | None,
    station_id: str | None,
    assigned_io: str | None,
    search: str | None,
    date_from: date | None,
    date_to: date | None,
    limit: int,
    offset: int,
) -> list[FIR]:
    statement = select(FIR)
    if viewer.role == RoleName.INVESTIGATING_OFFICER:
        statement = statement.where(FIR.assigned_io == viewer.user_id)
    elif viewer.role == RoleName.CITIZEN:
        statement = statement.join(Complaint, Complaint.complaint_id == FIR.complaint_id).where(
            Complaint.complainant_user_id == viewer.user_id
        )
    if status_filter:
        statement = statement.where(FIR.status == status_filter)
    if station_id:
        statement = statement.where(FIR.station_id == station_id)
    if assigned_io:
        statement = statement.where(FIR.assigned_io == assigned_io)
    if search:
        statement = statement.where(FIR.fir_number.contains(search, autoescape=True))
    if date_from:
        statement = statement.where(FIR.created_at >= datetime.combine(date_from, time.min, tzinfo=timezone.utc))
    if date_to:
        statement = statement.where(
            FIR.created_at < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc)
        )
    statement = statement.order_by(FIR.created_at.desc()).offset(offset).limit(limit)
    return list(session.exec(statement))


# ---------------------------------------------------------------- workflow


def _load(session: Session, fir_id: str) -> FIR:
    fir = session.get(FIR, fir_id)
    if not fir:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "FIR not found")
    return fir


def _require_assigned_io(fir: FIR, actor: User) -> None:
    if fir.assigned_io != actor.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This FIR is not assigned to you")


def _move(session: Session, fir: FIR, new_status: FIRStatus, actor: User, action: str, detail: str | None = None) -> None:
    if new_status not in FIR_TRANSITIONS[fir.status]:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"An FIR that is '{fir.status.value}' cannot move to '{new_status.value}'",
        )
    old = fir.status
    fir.status = new_status
    fir.updated_at = utcnow()
    if new_status == FIRStatus.CLOSED:
        fir.closed_at = fir.updated_at
    session.add(fir)
    log_event(
        session, entity_type="fir", entity_id=fir.fir_id, action=action, actor=actor,
        from_status=old.value, to_status=new_status.value, detail=detail,
    )


def assign_investigating_officer(session: Session, fir_id: str, io_user_id: str, actor: User) -> FIR:
    fir = _load(session, fir_id)
    io = session.get(User, io_user_id)
    if not io or io.role != RoleName.INVESTIGATING_OFFICER or not io.is_active:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "The selected user is not an active Investigating Officer")

    previous = fir.assigned_io
    _move(session, fir, FIRStatus.ASSIGNED, actor, "io_assigned" if previous is None else "io_reassigned",
          detail=f"assigned_io={io_user_id}" + (f" (was {previous})" if previous else ""))
    fir.assigned_io = io_user_id
    commit_or_conflict(session)
    session.refresh(fir)
    return fir


def start_investigation(session: Session, fir_id: str, actor: User) -> FIR:
    fir = _load(session, fir_id)
    _require_assigned_io(fir, actor)
    _move(session, fir, FIRStatus.INVESTIGATION_IN_PROGRESS, actor, "investigation_started")
    commit_or_conflict(session)
    session.refresh(fir)
    return fir


def submit_for_review(session: Session, fir_id: str, actor: User) -> FIR:
    fir = _load(session, fir_id)
    _require_assigned_io(fir, actor)
    _move(session, fir, FIRStatus.PENDING_REVIEW, actor, "submitted_for_review")
    commit_or_conflict(session)
    session.refresh(fir)
    return fir


def close_fir(session: Session, fir_id: str, actor: User) -> FIR:
    fir = _load(session, fir_id)
    _move(session, fir, FIRStatus.CLOSED, actor, "fir_closed")
    commit_or_conflict(session)
    session.refresh(fir)
    return fir


def return_to_investigation(session: Session, fir_id: str, reason: str, actor: User) -> FIR:
    fir = _load(session, fir_id)
    _move(session, fir, FIRStatus.INVESTIGATION_IN_PROGRESS, actor, "returned_to_investigation", detail=reason)
    commit_or_conflict(session)
    session.refresh(fir)
    return fir