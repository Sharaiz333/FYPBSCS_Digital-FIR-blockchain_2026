from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import require_role
from app.models.enums import ComplaintStatus, RoleName
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintRead, ReasonBody
from app.schemas.fir import FIRRead
from app.services import complaint_service
from app.services.fir_service import build_fir_reads

router = APIRouter(prefix="/complaints", tags=["complaints"])

# Citizens file their own; a Police Officer files for a walk-in complainant.
CAN_FILE = (RoleName.CITIZEN, RoleName.POLICE_OFFICER)
# Police staff review complaints. A citizen sees only their own.
CAN_VIEW = (RoleName.CITIZEN, RoleName.POLICE_OFFICER, RoleName.SUPERVISORY_OFFICER)
CAN_REVIEW = (RoleName.POLICE_OFFICER, RoleName.SUPERVISORY_OFFICER)


@router.post("", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
def file_complaint(
    payload: ComplaintCreate,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(*CAN_FILE)),
):
    complaint = complaint_service.create_complaint(session, payload, actor)
    return complaint_service.to_complaint_reads(session, [complaint])[0]


@router.get("", response_model=list[ComplaintRead])
def list_complaints(
    status_filter: ComplaintStatus | None = None,
    station_id: str | None = None,
    search: str | None = Query(default=None, max_length=50),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
    viewer: User = Depends(require_role(*CAN_VIEW)),
):
    complaints = complaint_service.list_complaints(
        session, viewer, status_filter=status_filter, station_id=station_id,
        search=search, limit=limit, offset=offset,
    )
    return complaint_service.to_complaint_reads(session, complaints)


@router.get("/{complaint_id}", response_model=ComplaintRead)
def get_complaint(
    complaint_id: str,
    session: Session = Depends(get_session),
    viewer: User = Depends(require_role(*CAN_VIEW)),
):
    complaint = complaint_service.get_complaint_for_viewer(session, complaint_id, viewer)
    return complaint_service.to_complaint_reads(session, [complaint])[0]


@router.post("/{complaint_id}/start-review", response_model=ComplaintRead)
def start_review(
    complaint_id: str,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(*CAN_REVIEW)),
):
    complaint = complaint_service.start_review(session, complaint_id, actor)
    return complaint_service.to_complaint_reads(session, [complaint])[0]


@router.post("/{complaint_id}/register", response_model=FIRRead, status_code=status.HTTP_201_CREATED)
def register_complaint_as_fir(
    complaint_id: str,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(*CAN_REVIEW)),
):
    """Review passed: create the FIR (and its FIR number) from this complaint."""
    fir = complaint_service.register_complaint(session, complaint_id, actor)
    return build_fir_reads(session, [fir])[0]


@router.post("/{complaint_id}/reject", response_model=ComplaintRead)
def reject_complaint(
    complaint_id: str,
    body: ReasonBody,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(*CAN_REVIEW)),
):
    complaint = complaint_service.reject_complaint(session, complaint_id, body.reason, actor)
    return complaint_service.to_complaint_reads(session, [complaint])[0]