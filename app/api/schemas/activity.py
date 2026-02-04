import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ActivityEventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    message: str
    zone_id: str | None = None
    plant_id: str | None = None
    sensor_id: str | None = None


class ActivityEventCreate(ActivityEventBase):
    occurred_at: datetime | None = None


class ActivityEvent(ActivityEventBase):
    id: uuid.UUID
    zone_id: uuid.UUID | None = None
    plant_id: uuid.UUID | None = None
    sensor_id: uuid.UUID | None = None
    occurred_at: datetime
