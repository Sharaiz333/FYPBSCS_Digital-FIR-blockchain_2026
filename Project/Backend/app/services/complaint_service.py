from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.complaint import Complaint
from app.models.enums import COMPLAINT_TRANSITIONS, ComplaintStatus, FIRStatus, RoleName
from app.models.fir import FIR
from app.models.station import PoliceStation
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintRead
from app.services.audit_service import log_event
from app.services.common import commit_or_conflict, utcnow
from app.services.numbering import next_reference


def can_view_complaint(viewer: User, complaint: Complaint) -> bool:
    if viewer.role in (RoleName.POLICE_OFFICER, RoleName.SUPERVISORY_OFFICER):
        return True
    if viewer.role == RoleName.CITIZEN:
        return complaint.complainant_user_id == viewer.user_id
    return False


def get_complaint_for_viewer(session: Session, complaint_id: str, viewer: User) -> Complaint:
    complaint = session.get(Complaint, complaint_id)
    # 404 (not 403) when it isn't yours: don't confirm that someone else's record exists.
    if not complaint or not can_view_complaint(viewer, complaint):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Complaint not found")
    return complaint


def to_complaint_reads(session: Session, complaints: list[Complaint]) -> list[ComplaintRead]:
    ids = [c.complaint_id for c in complaints]
    firs = session.exec(select(FIR).where(FIR.complaint_id.in_(ids))).all() if ids else []
    fir_by_complaint = {f.complaint_id: f for f in firs}
    reads = []
    for complaint in complaints:
        read = ComplaintRead.model_validate(complaint)
        fir = fir_by_complaint.get(complaint.complaint_id)
        if fir:
            read.fir_id, read.fir_number = fir.fir_id, fir.fir_number
        reads.append(read)
    return reads


def create_complaint(session: Session, data: ComplaintCreate, actor: User) -> Complaint:
    station = session.get(PoliceStation, data.station_id)
    if not station or not station.is_active:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown or inactive police station")

    # A police officer filing here is recording a walk-in complainant's complaint;
    # a citizen is filing their own.
    on_behalf = actor.role == RoleName.POLICE_OFFICER
    complaint = Complaint(
        reference_number=next_reference(session, Complaint.reference_number, "CMP"),
        **data.model_dump(),
        complainant_user_id=None if on_behalf else actor.user_id,
        filed_by_user_id=actor.user_id,
        filed_on_behalf=on_behalf,
        status=ComplaintStatus.SUBMITTED,
    )
    session.add(complaint)
    log_event(
        session,
        entity_type="complaint",
        entity_id=complaint.complaint_id,
        action="complaint_submitted",
        actor=actor,
        to_status=ComplaintStatus.SUBMITTED.value,
        detail="filed on behalf of a walk-in complainant" if on_behalf else None,
    )
    commit_or_conflict(session)
    session.refresh(complaint)
    return complaint


def list_complaints(
    session: Session,
    viewer: User,
    *,
    status_filter: ComplaintStatus | None,
    station_id: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> list[Complaint]:
    statement = select(Complaint)
    if viewer.role == RoleName.CITIZEN:
        statement = statement.where(Complaint.complainant_user_id == viewer.user_id)
    if status_filter:
        statement = statement.where(Complaint.status == status_filter)
    if station_id:
        statement = statement.where(Complaint.station_id == station_id)
    if search:
        statement = statement.where(Complaint.reference_number.contains(search, autoescape=True))
    statement = statement.order_by(Complaint.created_at.desc()).offset(offset).limit(limit)
    return list(session.exec(statement))


def _change_status(
    session: Session, complaint: Complaint, new_status: ComplaintStatus, actor: User, action: str,
    detail: str | None = None,
) -> None:
    if new_status not in COMPLAINT_TRANSITIONS[complaint.status]:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"A complaint that is '{complaint.status.value}' cannot move to '{new_status.value}'",
        )
    old = complaint.status
    complaint.status = new_status
    complaint.reviewed_by = actor.user_id
    complaint.updated_at = utcnow()
    session.add(complaint)
    log_event(
        session, entity_type="complaint", entity_id=complaint.complaint_id, action=action,
        actor=actor, from_status=old.value, to_status=new_status.value, detail=detail,
    )


def start_review(session: Session, complaint_id: str, actor: User) -> Complaint:
    complaint = get_complaint_for_viewer(session, complaint_id, actor)
    _change_status(session, complaint, ComplaintStatus.UNDER_REVIEW, actor, "review_started")
    commit_or_conflict(session)
    session.refresh(complaint)
    return complaint


def reject_complaint(session: Session, complaint_id: str, reason: str, actor: User) -> Complaint:
    complaint = get_complaint_for_viewer(session, complaint_id, actor)
    _change_status(session, complaint, ComplaintStatus.REJECTED, actor, "complaint_rejected", detail=reason)
    complaint.rejection_reason = reason
    commit_or_conflict(session)
    session.refresh(complaint)
    return complaint


def register_complaint(session: Session, complaint_id: str, actor: User) -> FIR:
    """Proposal Step 4: review passed, so an FIR is created and given its number."""
    complaint = get_complaint_for_viewer(session, complaint_id, actor)
    _change_status(session, complaint, ComplaintStatus.REGISTERED, actor, "complaint_registered")

    fir = FIR(
        fir_number=next_reference(session, FIR.fir_number, "FIR"),
        complaint_id=complaint.complaint_id,
        station_id=complaint.station_id,
        crime_category=complaint.crime_category,
        incident_date=complaint.incident_date,
        incident_location=complaint.incident_location,
        description=complaint.description,
        status=FIRStatus.REGISTERED,
        registered_by=actor.user_id,
    )
    session.add(fir)
    log_event(
        session, entity_type="fir", entity_id=fir.fir_id, action="fir_registered", actor=actor,
        to_status=FIRStatus.REGISTERED.value, detail=f"created from complaint {complaint.reference_number}",
    )
    commit_or_conflict(session)
    session.refresh(fir)
    return fir