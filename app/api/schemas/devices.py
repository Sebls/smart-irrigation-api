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
