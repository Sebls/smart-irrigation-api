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
    created_at: datetime
    updated_at: datetime


class ProvisionSensor(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    local_name: str
    type: SensorType


class ProvisionCapabilities(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    sensors: list[ProvisionSensor]
    cameras: list[str] = []


class ProvisionRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    hardware_id: str
    firmware: str
    capabilities: ProvisionCapabilities


class ProvisionSensorResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    local_name: str
    sensor_id: uuid.UUID
    type: SensorType
    unit: str


class ProvisionCameraResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    local_name: str
    camera_id: uuid.UUID


class ProvisionResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    device_id: uuid.UUID
    timezone: str = "Europe/Paris"
    location: dict | None = None
    polling: dict = {"telemetryIntervalSec": 60, "heartbeatIntervalSec": 30}
    sensors: list[ProvisionSensorResponse]
    cameras: list[ProvisionCameraResponse]
