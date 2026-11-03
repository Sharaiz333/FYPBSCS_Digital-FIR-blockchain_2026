from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FIRStatus


class ComplainantInfo(BaseModel):
    name: str
    cnic: str
    phone: str
    address: str | None


class FIRRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fir_id: str
    fir_number: str
    complaint_id: str
    complaint_reference: str | None = None
    station_id: str
    crime_category: str
    incident_date: datetime
    incident_location: str
    description: str
    status: FIRStatus
    assigned_io: str | None
    assigned_io_name: str | None = None
    registered_by: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    # Only present on the single-FIR endpoint, and only for roles allowed to see personal data.
    complainant: ComplainantInfo | None = None


class AssignIORequest(BaseModel):
    io_user_id: str = Field(min_length=1)