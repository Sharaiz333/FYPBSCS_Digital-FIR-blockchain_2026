from pydantic import BaseModel, ConfigDict, Field


class StationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str | None = Field(default=None, max_length=200)


class StationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    station_id: str
    name: str
    location: str | None
    is_active: bool