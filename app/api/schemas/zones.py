import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ZoneBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    is_active: bool = False


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    is_active: bool | None = None


class Zone(ZoneBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
