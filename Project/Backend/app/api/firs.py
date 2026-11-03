from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import require_role
from app.models.enums import FIRStatus, RoleName
from app.models.user import User
from app.schemas.complaint import ReasonBody
from app.schemas.fir import AssignIORequest, FIRRead
from app.services import fir_service

router = APIRouter(prefix="/firs", tags=["firs"])

# Admin is deliberately absent: administrators manage users and the system,
# not case content (least privilege).
CAN_VIEW = (
    RoleName.CITIZEN,
    RoleName.POLICE_OFFICER,
    RoleName.INVESTIGATING_OFFICER,
    RoleName.SUPERVISORY_OFFICER,
    RoleName.AUDIT_REVIEW_OFFICER,
)


@router.get("", response_model=list[FIRRead])
def list_firs(
    status_filter: FIRStatus | None = None,
    station_id: str | None = None,
    assigned_io: str | None = None,
    search: str | None = Query(default=None, max_length=50),
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
    viewer: User = Depends(require_role(*CAN_VIEW)),
):
    firs = fir_service.list_firs(
        session, viewer, status_filter=status_filter, station_id=station_id, assigned_io=assigned_io,
        search=search, date_from=date_from, date_to=date_to, limit=limit, offset=offset,
    )
    return fir_service.build_fir_reads(session, firs)


@router.get("/{fir_id}", response_model=FIRRead)
def get_fir(
    fir_id: str,
    session: Session = Depends(get_session),
    viewer: User = Depends(require_role(*CAN_VIEW)),
):
    fir, complaint = fir_service.get_fir_for_viewer(session, fir_id, viewer)
    return fir_service.build_fir_detail(session, fir, complaint, viewer)


@router.post("/{fir_id}/assign", response_model=FIRRead)
def assign_io(
    fir_id: str,
    body: AssignIORequest,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(RoleName.SUPERVISORY_OFFICER)),
):
    fir = fir_service.assign_investigating_officer(session, fir_id, body.io_user_id, actor)
    return fir_service.build_fir_reads(session, [fir])[0]


@router.post("/{fir_id}/start-investigation", response_model=FIRRead)
def start_investigation(
    fir_id: str,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(RoleName.INVESTIGATING_OFFICER)),
):
    fir = fir_service.start_investigation(session, fir_id, actor)
    return fir_service.build_fir_reads(session, [fir])[0]


@router.post("/{fir_id}/submit-for-review", response_model=FIRRead)
def submit_for_review(
    fir_id: str,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(RoleName.INVESTIGATING_OFFICER)),
):
    fir = fir_service.submit_for_review(session, fir_id, actor)
    return fir_service.build_fir_reads(session, [fir])[0]


@router.post("/{fir_id}/close", response_model=FIRRead)
def close_fir(
    fir_id: str,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(RoleName.SUPERVISORY_OFFICER)),
):
    fir = fir_service.close_fir(session, fir_id, actor)
    return fir_service.build_fir_reads(session, [fir])[0]


@router.post("/{fir_id}/return-to-investigation", response_model=FIRRead)
def return_to_investigation(
    fir_id: str,
    body: ReasonBody,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role(RoleName.SUPERVISORY_OFFICER)),
):
    fir = fir_service.return_to_investigation(session, fir_id, body.reason, actor)
    return fir_service.build_fir_reads(session, [fir])[0]