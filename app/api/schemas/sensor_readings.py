import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SensorReadingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sensor_id: str
    value: float


class SensorReadingCreate(SensorReadingBase):
    recorded_at: datetime | None = None


class SensorReading(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    sensor_id: uuid.UUID
    recorded_at: datetime
    value: float
