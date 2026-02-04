import logging
import uuid
from sqlalchemy.orm import Session
from app.api.schemas.devices import TelemetryRequest, TelemetryResponse
from app.api.schemas.sensor_readings import SensorReadingCreate
from app.api.services import sensor_readings_service
from app.infrastructure.models.sensors import SensorModel


logger = logging.getLogger(__name__)


def save_telemetry(
    db: Session, request: TelemetryRequest, device_uuid: uuid.UUID
) -> TelemetryResponse:
    processed_count = 0

    for reading in request.readings:
        # Try to find sensor by ID (UUID) or by Name
        db_sensor = None
        try:
            sensor_uuid = uuid.UUID(reading.sensor_id)
            db_sensor = (
                db.query(SensorModel)
                .filter(SensorModel.id == sensor_uuid, SensorModel.deleted_at.is_(None))
                .first()
            )
        except ValueError:
            # Not a UUID, will be handled by the warning below
            pass

        if db_sensor:
            # Create reading
            reading_data = SensorReadingCreate(
                sensor_id=str(db_sensor.id),
                value=reading.value,
                recorded_at=reading.reading_at or request.sent_at,
            )
            sensor_readings_service.create_sensor_reading(db, reading_data)
            processed_count += 1
        else:
            logger.warning(
                "Unknown sensor in telemetry: Data don't will be saved",
                extra={"sensor_id": reading.sensor_id, "device_id": device_uuid},
            )

    return TelemetryResponse(
        id=uuid.uuid4(),
        device_id=str(device_uuid),
        status="accepted",
        processed_count=processed_count,
    )
