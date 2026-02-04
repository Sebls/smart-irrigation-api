import json
import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.api.schemas.devices import (
    TelemetryRequest,
    TelemetryResponse,
    DeviceLogCreate,
    DeviceLogResponse,
    DeviceImageCreate,
    DeviceImageResponse,
    DeviceStatusResponse,
    DeviceCreate,
    DeviceUpdate,
    Device,
)
from app.api.schemas.sensor_readings import SensorReadingCreate
from app.api.services import sensor_readings_service
from app.infrastructure.models.sensors import SensorModel
from app.infrastructure.models.devices import (
    DeviceModel,
    DeviceLogModel,
    DeviceImageModel,
)


logger = logging.getLogger(__name__)


def _get_or_create_device(db: Session, device_uuid: uuid.UUID) -> DeviceModel:
    device = db.query(DeviceModel).filter(DeviceModel.id == device_uuid).first()
    if not device:
        device = DeviceModel(
            id=device_uuid,
            name=f"Device {str(device_uuid)[:8]}",
            is_active=True,
            is_online=True,
            last_seen_at=datetime.utcnow(),
        )
        db.add(device)
        db.commit()
        db.refresh(device)
    else:
        device.last_seen_at = datetime.utcnow()
        device.is_online = True
        db.commit()
    return device


def save_telemetry(
    db: Session, request: TelemetryRequest, device_uuid: uuid.UUID
) -> TelemetryResponse:
    # Track device liveness
    _get_or_create_device(db, device_uuid)

    processed_count = 0
    for reading in request.readings:
        # Try to find sensor by ID (UUID)
        db_sensor = None
        try:
            sensor_uuid = uuid.UUID(reading.sensor_id)
            db_sensor = (
                db.query(SensorModel)
                .filter(SensorModel.id == sensor_uuid, SensorModel.deleted_at.is_(None))
                .first()
            )
        except ValueError:
            pass

        if db_sensor:
            reading_data = SensorReadingCreate(
                sensor_id=str(db_sensor.id),
                value=reading.value,
                recorded_at=reading.reading_at or request.sent_at,
            )
            sensor_readings_service.create_sensor_reading(db, reading_data)
            processed_count += 1
        else:
            logger.warning(
                "Unknown sensor in telemetry: Data won't be saved",
                extra={"sensor_id": reading.sensor_id, "device_id": device_uuid},
            )

    return TelemetryResponse(
        id=uuid.uuid4(),
        device_id=str(device_uuid),
        status="accepted",
        processed_count=processed_count,
    )


def save_log(
    db: Session, device_id: uuid.UUID, request: DeviceLogCreate
) -> DeviceLogResponse:
    _get_or_create_device(db, device_id)

    db_log = DeviceLogModel(
        device_id=device_id,
        level=request.level,
        message=request.message,
        recorded_at=request.recorded_at or datetime.utcnow(),
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return DeviceLogResponse(
        id=db_log.id,
        device_id=db_log.device_id,
        level=db_log.level,
        message=db_log.message,
        recorded_at=db_log.recorded_at,
    )


def save_image(
    db: Session, device_id: uuid.UUID, request: DeviceImageCreate
) -> DeviceImageResponse:
    import base64
    import os

    _get_or_create_device(db, device_id)

    # 1. Prepare Storage
    upload_dir = os.path.join("uploads", "devices", str(device_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{request.type}.jpg")

    # 2. Decode and Save Image
    try:
        # Handle data:image/jpeg;base64,... prefix if present
        header = "base64,"
        if header in request.image_base64:
            image_data = request.image_base64.split(header)[1]
        else:
            image_data = request.image_base64

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_data))
    except Exception as e:
        logger.error(f"Failed to save image to disk: {str(e)}")
        raise e

    # 3. Database Upsert (One live image per type per device)
    db_image = (
        db.query(DeviceImageModel)
        .filter(
            DeviceImageModel.device_id == device_id,
            DeviceImageModel.type == request.type,
        )
        .first()
    )

    if db_image:
        db_image.plant_id = request.plant_id
        db_image.zone_id = request.zone_id
        db_image.image_url = file_path
        db_image.captured_at = request.captured_at
        db_image.metadata_json = (
            json.dumps(request.metadata) if request.metadata else None
        )
    else:
        db_image = DeviceImageModel(
            device_id=device_id,
            plant_id=request.plant_id,
            zone_id=request.zone_id,
            image_url=file_path,
            type=request.type,
            captured_at=request.captured_at,
            metadata_json=json.dumps(request.metadata) if request.metadata else None,
        )
        db.add(db_image)

    db.commit()
    db.refresh(db_image)

    return DeviceImageResponse(
        id=db_image.id,
        device_id=db_image.device_id,
        plant_id=db_image.plant_id,
        zone_id=db_image.zone_id,
        image_url=db_image.image_url,
        type=db_image.type,
        captured_at=db_image.captured_at,
    )


def get_device_status(db: Session, device_id: uuid.UUID) -> DeviceStatusResponse:
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        # If device has never sent anything, it's offline and unknown
        return DeviceStatusResponse(
            device_id=device_id,
            name="Unknown Device",
            is_online=False,
            last_seen_at=None,
            uptime=None,
        )

    # Simple logic: if last seen > 5 minutes ago, consider offline
    # In a real app, this might be based on a heartbeat
    is_online = False
    if device.last_seen_at:
        delta = datetime.utcnow() - device.last_seen_at
        is_online = delta.total_seconds() < 300  # 5 minutes

    return DeviceStatusResponse(
        device_id=device.id,
        name=device.name,
        is_online=is_online,
        last_seen_at=device.last_seen_at,
        uptime=device.uptime,
    )


def create_device(db: Session, device: DeviceCreate) -> Device:
    db_device = DeviceModel(
        name=device.name,
        description=device.description,
        is_active=device.is_active,
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return Device.model_validate(db_device)


def get_devices(db: Session) -> list[Device]:
    db_devices = db.query(DeviceModel).all()
    return [Device.model_validate(device) for device in db_devices]


def get_device(db: Session, device_id: uuid.UUID) -> Device | None:
    db_device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not db_device:
        return None
    return Device.model_validate(db_device)


def update_device(
    db: Session, device_id: uuid.UUID, device: DeviceUpdate
) -> Device | None:
    db_device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not db_device:
        return None

    data = device.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_device, key, value)

    db.commit()
    db.refresh(db_device)
    return Device.model_validate(db_device)


def delete_device(db: Session, device_id: uuid.UUID) -> Device | None:
    db_device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not db_device:
        return None

    db.delete(db_device)
    db.commit()
    return Device.model_validate(db_device)
