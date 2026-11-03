import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.models.enums import FIRStatus


class FIR(SQLModel, table=True):
    """Created only when police approve a complaint. It copies the incident
    facts so the FIR is a self-contained record (this is the record that
    will be hashed at verification in a later stage). The complainant's
    personal data is NOT copied: it stays on the linked complaint."""

    __tablename__ = "firs"

    fir_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    fir_number: str = Field(index=True, unique=True)  # FIR-2026-000001
    complaint_id: str = Field(foreign_key="complaints.complaint_id", unique=True)
    station_id: str = Field(foreign_key="police_stations.station_id", index=True)

    crime_category: str
    incident_date: datetime
    incident_location: str
    description: str

    status: FIRStatus = Field(default=FIRStatus.REGISTERED, index=True)
    assigned_io: str | None = Field(default=None, foreign_key="users.user_id", index=True)
    registered_by: str = Field(foreign_key="users.user_id")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None