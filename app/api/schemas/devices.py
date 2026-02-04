import uuid
from pydantic import BaseModel, AliasGenerator, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime
from enum import Enum


class SensorType(str, Enum):
    humidity = "humidity"
    temperature = "temperature"
    flow = "flow"
    water_level = "water-level"
    air_quality = "air-quality"


class SensorReading(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    sensor_id: str
    type: SensorType
    value: float
    unit: str
    reading_at: datetime | None = None


class TelemetryRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    sent_at: datetime
    readings: list[SensorReading]


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    id: uuid.UUID
    device_id: str
    status: str = "accepted"
    processed_count: int


class DeviceLogCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    level: str
    message: str
    recorded_at: datetime | None = None


class DeviceLogResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    id: uuid.UUID
    device_id: uuid.UUID
    level: str
    message: str
    recorded_at: datetime


class DeviceImageCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    plant_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    image_base64: str
    type: str  # plant, tank, zone
    captured_at: datetime
    metadata: dict | None = None


class DeviceImageResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    id: uuid.UUID
    device_id: uuid.UUID
    plant_id: uuid.UUID | None
    zone_id: uuid.UUID | None
    image_url: str
    type: str
    captured_at: datetime


class DeviceStatusResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    device_id: uuid.UUID
    name: str
    is_online: bool
    last_seen_at: datetime | None
    uptime: float | None


class DeviceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    is_active: bool = True


class DeviceUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class Device(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    last_seen_at: datetime | None
    is_online: bool
    uptime: float | None
    created_at: datetime
    updated_at: datetime
