import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SensorBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    type: str  # humidity, temperature, air-quality
    unit: str
    is_active: bool = True
    plant_id: str | None = None
    zone_id: str | None = None


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    type: str | None = None
    unit: str | None = None
    is_active: bool | None = None
    plant_id: str | None = None
    zone_id: str | None = None


class Sensor(SensorBase):
    id: uuid.UUID
    plant_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
