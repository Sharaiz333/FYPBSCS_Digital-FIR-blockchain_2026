from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import require_role
from app.models.enums import RoleName, VerificationStatus
from app.models.user import User
from app.schemas.verification import PendingCitizenRead, VerificationDecision

router = APIRouter(prefix="/verification", tags=["verification"])

# Only police staff may vouch for a citizen's identity.
CAN_VERIFY = (RoleName.POLICE_OFFICER, RoleName.SUPERVISORY_OFFICER)


@router.get("/citizens", response_model=list[PendingCitizenRead])
def list_citizens_for_verification(
    status_filter: VerificationStatus = VerificationStatus.PENDING,
    session: Session = Depends(get_session),
    _officer: User = Depends(require_role(*CAN_VERIFY)),
):
    statement = (
        select(User)
        .where(User.role == RoleName.CITIZEN, User.verification_status == status_filter)
        .order_by(User.created_at)
    )
    return session.exec(statement).all()


@router.post("/citizens/{user_id}", response_model=PendingCitizenRead)
def decide_citizen_registration(
    user_id: str,
    decision: VerificationDecision,
    session: Session = Depends(get_session),
    officer: User = Depends(require_role(*CAN_VERIFY)),
):
    citizen = session.get(User, user_id)
    if not citizen or citizen.role != RoleName.CITIZEN:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Citizen registration not found")
    if citizen.verification_status != VerificationStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "This registration has already been decided")
    if not decision.approve and not (decision.reason and decision.reason.strip()):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "A reason is required to reject a registration")

    citizen.verification_status = VerificationStatus.VERIFIED if decision.approve else VerificationStatus.REJECTED
    citizen.verified_by = officer.user_id
    citizen.verified_at = datetime.now(timezone.utc)
    citizen.rejection_reason = None if decision.approve else decision.reason.strip()
    session.add(citizen)
    session.commit()
    session.refresh(citizen)
    return citizen