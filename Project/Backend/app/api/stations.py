from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import get_current_user, require_role
from app.models.enums import RoleName
from app.models.station import PoliceStation
from app.models.user import User
from app.schemas.station import StationCreate, StationRead

router = APIRouter(prefix="/stations", tags=["stations"])


@router.post("", response_model=StationRead, status_code=status.HTTP_201_CREATED)
def create_station(
    payload: StationCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_role(RoleName.ADMIN)),
):
    station = PoliceStation(name=payload.name.strip(), location=payload.location)
    session.add(station)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "A station with this name already exists")
    session.refresh(station)
    return station


@router.get("", response_model=list[StationRead])
def list_stations(
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
):
    """Any logged-in user: citizens need this list to file a complaint."""
    return session.exec(select(PoliceStation).where(PoliceStation.is_active == True).order_by(PoliceStation.name)).all()  # noqa: E712