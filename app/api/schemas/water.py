import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


class WaterTankBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    capacity_liters: int


class WaterTankCreate(WaterTankBase):
    pass


class WaterTankUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    capacity_liters: int | None = None


class WaterTank(WaterTankBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class WaterTankReadingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tank_id: str
    level_percent: Decimal
    current_liters: Decimal


class WaterTankReadingCreate(WaterTankReadingBase):
    recorded_at: datetime | None = None


class WaterTankReading(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tank_id: uuid.UUID
    recorded_at: datetime
    level_percent: Decimal
    current_liters: Decimal
