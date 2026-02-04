import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class IrrigationJobBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    scope: str  # zone or plant
    zone_id: str | None = None
    plant_id: str | None = None
    action: str  # start or stop
    duration_seconds: int | None = None
    status: str = "accepted"  # accepted, running, completed, failed, cancelled


class IrrigationJobCreate(IrrigationJobBase):
    pass


class IrrigationJobUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error_message: str | None = None


class IrrigationJob(IrrigationJobBase):
    id: uuid.UUID
    zone_id: uuid.UUID | None = None
    plant_id: uuid.UUID | None = None
    requested_at: datetime
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error_message: str | None = None
