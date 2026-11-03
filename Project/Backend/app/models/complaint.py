import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.models.enums import ComplaintStatus


class Complaint(SQLModel, table=True):
    """The citizen's (or a walk-in complainant's) original complaint.
    An FIR is only created from it after police review (proposal Steps 1-4).
    All personal data lives here, off-chain."""

    __tablename__ = "complaints"

    complaint_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    reference_number: str = Field(index=True, unique=True)  # CMP-2026-000001

    station_id: str = Field(foreign_key="police_stations.station_id", index=True)
    crime_category: str
    incident_date: datetime
    incident_location: str
    description: str
    suspect_details: str | None = None
    witness_details: str | None = None

    # The complainant's own details, stored on the complaint itself so that a
    # walk-in complainant (who has no account) is handled exactly like a citizen.
    complainant_name: str
    complainant_cnic: str
    complainant_phone: str
    complainant_address: str | None = None

    # Set only when the complainant filed it through their own account.
    complainant_user_id: str | None = Field(default=None, foreign_key="users.user_id", index=True)
    # Who actually typed it in. For a walk-in this is the police officer.
    filed_by_user_id: str = Field(foreign_key="users.user_id")
    filed_on_behalf: bool = Field(default=False)

    status: ComplaintStatus = Field(default=ComplaintStatus.SUBMITTED, index=True)
    reviewed_by: str | None = Field(default=None, foreign_key="users.user_id")
    rejection_reason: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))