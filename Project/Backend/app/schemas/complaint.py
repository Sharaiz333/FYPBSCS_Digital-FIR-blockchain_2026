from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ComplaintStatus

CNIC_PATTERN = r"^\d{5}-\d{7}-\d$"
PHONE_PATTERN = r"^03\d{2}-?\d{7}$"


class ComplaintCreate(BaseModel):
    # Trim leading/trailing spaces BEFORE the length checks run.
    model_config = ConfigDict(str_strip_whitespace=True)

    station_id: str
    crime_category: str = Field(min_length=2, max_length=100)
    incident_date: datetime
    incident_location: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=20, max_length=2000)
    suspect_details: str | None = Field(default=None, max_length=1000)
    witness_details: str | None = Field(default=None, max_length=1000)
    complainant_name: str = Field(min_length=2, max_length=100)
    complainant_cnic: str = Field(pattern=CNIC_PATTERN)
    complainant_phone: str = Field(pattern=PHONE_PATTERN)
    complainant_address: str | None = Field(default=None, max_length=200)

    @field_validator("incident_date")
    @classmethod
    def incident_not_in_future(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        # 5 minutes of tolerance for small clock differences between devices.
        if value > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("The incident date cannot be in the future")
        return value


class ReasonBody(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reason: str = Field(min_length=3, max_length=300)


class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complaint_id: str
    reference_number: str
    station_id: str
    crime_category: str
    incident_date: datetime
    incident_location: str
    description: str
    suspect_details: str | None
    witness_details: str | None
    complainant_name: str
    complainant_cnic: str
    complainant_phone: str
    complainant_address: str | None
    complainant_user_id: str | None
    filed_by_user_id: str
    filed_on_behalf: bool
    status: ComplaintStatus
    reviewed_by: str | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime
    # Filled in once an FIR has been created from this complaint.
    fir_id: str | None = None
    fir_number: str | None = None