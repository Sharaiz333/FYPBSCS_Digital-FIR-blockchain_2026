import uuid

from sqlmodel import Field, SQLModel


class PoliceStation(SQLModel, table=True):
    __tablename__ = "police_stations"

    station_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True, unique=True)
    location: str | None = None
    is_active: bool = Field(default=True)