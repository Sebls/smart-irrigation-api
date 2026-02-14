import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
import mimetypes
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.infrastructure.models.devices import (
    DeviceModel,
    DeviceLogModel,
    DeviceImageModel,
)
from app.infrastructure.models.zones import ZoneModel
from app.infrastructure.models.sensors import SensorModel
from app.api.schemas.sensor_readings import SensorReadingCreate
from app.api.services import sensor_readings_service
from app.api.schemas.devices import (
    TelemetryRequest,
    TelemetryResponse,
    DeviceLogCreate,
    DeviceLogResponse,
    DeviceImageResponse,
    DeviceStatusResponse,
    DeviceCreate,
    DeviceUpdate,
    Device,
    ProvisionRequest,
    ProvisionResponse,
    ProvisionSensorResponse,
    ProvisionCameraResponse,
)


logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_UPLOADS_ROOT = (_REPO_ROOT / "uploads").resolve()


def _resolve_image_path(image_url: str) -> Path:
    """
    Resolve a DB `image_url` (relative or absolute) into an absolute path and
    ensure it stays within the `uploads/` directory for safety.
    """
    candidate = Path(image_url)
    abs_path = (candidate if candidate.is_absolute() else (_REPO_ROOT / candidate)).resolve()

    if abs_path != _UPLOADS_ROOT and _UPLOADS_ROOT not in abs_path.parents:
        raise ValueError("Invalid image path (outside uploads directory)")

    return abs_path


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
    db: Session,
    device_id: uuid.UUID,
    image_file: UploadFile,
    image_type: str,
    captured_at: datetime,
    plant_id: uuid.UUID | None = None,
    zone_id: uuid.UUID | None = None,
    metadata: dict | None = None,
) -> DeviceImageResponse:
    import os

    _get_or_create_device(db, device_id)

    # 1. Prepare Storage
    upload_dir_rel = os.path.join("uploads", "devices", str(device_id))
    upload_dir_abs = (_REPO_ROOT / upload_dir_rel).resolve()
    os.makedirs(upload_dir_abs, exist_ok=True)
    file_path_rel = os.path.join(upload_dir_rel, f"{image_type}.jpg")
    file_path_abs = (_REPO_ROOT / file_path_rel).resolve()

    # 2. Save Image File
    try:
        with open(file_path_abs, "wb") as f:
            f.write(image_file.file.read())
    except Exception as e:
        logger.error(f"Failed to save image to disk: {str(e)}")
        raise e

    # 3. Database Upsert (One live image per type per device)
    db_image = (
        db.query(DeviceImageModel)
        .filter(
            DeviceImageModel.device_id == device_id,
            DeviceImageModel.type == image_type,
        )
        .first()
    )

    if db_image:
        db_image.plant_id = plant_id
        db_image.zone_id = zone_id
        db_image.image_url = file_path_rel
        db_image.captured_at = captured_at
        db_image.metadata_json = json.dumps(metadata) if metadata else None
    else:
        db_image = DeviceImageModel(
            device_id=device_id,
            plant_id=plant_id,
            zone_id=zone_id,
            image_url=file_path_rel,
            type=image_type,
            captured_at=captured_at,
            metadata_json=json.dumps(metadata) if metadata else None,
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


def list_device_images(db: Session, device_id: uuid.UUID) -> list[DeviceImageResponse]:
    images = (
        db.query(DeviceImageModel)
        .filter(DeviceImageModel.device_id == device_id)
        .order_by(DeviceImageModel.captured_at.desc())
        .all()
    )
    return [
        DeviceImageResponse(
            id=img.id,
            device_id=img.device_id,
            plant_id=img.plant_id,
            zone_id=img.zone_id,
            image_url=img.image_url,
            type=img.type,
            captured_at=img.captured_at,
        )
        for img in images
    ]


def get_device_image(db: Session, device_id: uuid.UUID, image_id: uuid.UUID) -> DeviceImageResponse | None:
    img = (
        db.query(DeviceImageModel)
        .filter(DeviceImageModel.id == image_id, DeviceImageModel.device_id == device_id)
        .first()
    )
    if not img:
        return None
    return DeviceImageResponse(
        id=img.id,
        device_id=img.device_id,
        plant_id=img.plant_id,
        zone_id=img.zone_id,
        image_url=img.image_url,
        type=img.type,
        captured_at=img.captured_at,
    )


def get_device_image_file(
    db: Session, device_id: uuid.UUID, image_id: uuid.UUID
) -> tuple[str, str, str]:
    """
    Returns (absolute_path, media_type, filename) for an image belonging to `device_id`.
    """
    img = (
        db.query(DeviceImageModel)
        .filter(DeviceImageModel.id == image_id, DeviceImageModel.device_id == device_id)
        .first()
    )
    if not img:
        raise FileNotFoundError("Image not found")

    abs_path = _resolve_image_path(img.image_url)
    if not abs_path.exists() or not abs_path.is_file():
        raise FileNotFoundError("Image file not found on disk")

    media_type = mimetypes.guess_type(str(abs_path))[0] or "application/octet-stream"
    safe_type = (img.type or "image").replace("/", "-")
    filename = f"{device_id}-{safe_type}.jpg"
    return str(abs_path), media_type, filename


def get_device_image_file_by_type(
    db: Session, device_id: uuid.UUID, image_type: str
) -> tuple[str, str, str]:
    """
    Returns (absolute_path, media_type, filename) for the latest image of `image_type`.
    Note: current ingestion upserts one row per type, so this generally returns the single record.
    """
    img = (
        db.query(DeviceImageModel)
        .filter(DeviceImageModel.device_id == device_id, DeviceImageModel.type == image_type)
        .order_by(DeviceImageModel.captured_at.desc())
        .first()
    )
    if not img:
        raise FileNotFoundError("Image not found")

    abs_path = _resolve_image_path(img.image_url)
    if not abs_path.exists() or not abs_path.is_file():
        raise FileNotFoundError("Image file not found on disk")

    media_type = mimetypes.guess_type(str(abs_path))[0] or "application/octet-stream"
    safe_type = (img.type or "image").replace("/", "-")
    filename = f"{device_id}-{safe_type}.jpg"
    return str(abs_path), media_type, filename


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


def provision_device(db: Session, request: ProvisionRequest) -> ProvisionResponse:
    # 1. Find or create device by hardware_id
    device = (
        db.query(DeviceModel)
        .filter(DeviceModel.hardware_id == request.hardware_id)
        .first()
    )

    if not device:
        device = DeviceModel(
            id=uuid.uuid4(),
            name=f"Device {request.hardware_id[:8]}",
            hardware_id=request.hardware_id,
            is_active=True,
            is_online=True,
            last_seen_at=datetime.utcnow(),
        )
        db.add(device)
        db.flush()  # Get the ID
    else:
        device.last_seen_at = datetime.utcnow()
        device.is_online = True

    # 2. Ensure default Zone exists for this device
    # For now, we create a default zone named "Home Zone" if none exists
    zone = (
        db.query(ZoneModel)
        .filter(ZoneModel.name == "Primary Zone", ZoneModel.deleted_at.is_(None))
        .first()
    )
    if not zone:
        zone = ZoneModel(name="Primary Zone", is_active=True)
        db.add(zone)
        db.flush()

    # 3. Ensure Water Tank exists
    # 3. Register Sensors
    sensor_responses = []
    for cap_sensor in request.capabilities.sensors:
        # Check if sensor already exists (by local name + device/zone context could be complex)
        # For simplicity in this implementation, we'll look for a sensor by name in this zone
        db_sensor = (
            db.query(SensorModel)
            .filter(
                SensorModel.name == f"{request.hardware_id}-{cap_sensor.local_name}",
                SensorModel.zone_id == zone.id,
                SensorModel.deleted_at.is_(None),
            )
            .first()
        )

        if not db_sensor:
            unit = (
                "%"
                if cap_sensor.type == "humidity"
                else "L/min"
                if cap_sensor.type == "flow"
                else "N/A"
            )
            db_sensor = SensorModel(
                id=uuid.uuid4(),
                name=f"{request.hardware_id}-{cap_sensor.local_name}",
                type=cap_sensor.type.value,
                unit=unit,
                zone_id=zone.id,
                is_active=True,
            )
            db.add(db_sensor)
            db.flush()

        sensor_responses.append(
            ProvisionSensorResponse(
                local_name=cap_sensor.local_name,
                sensor_id=db_sensor.id,
                type=cap_sensor.type,
                unit=db_sensor.unit,
            )
        )

    # 4. Cameras (Metadata only for now)
    camera_responses = []
    for cam_name in request.capabilities.cameras:
        # Check if image metadata already exists
        db_image = (
            db.query(DeviceImageModel)
            .filter(
                DeviceImageModel.device_id == device.id,
                DeviceImageModel.type == cam_name,
            )
            .first()
        )

        if not db_image:
            # We don't have an image yet, but we can register the expectation
            # For now, let's just return a placeholder UUID if we had a Camera model
            # Since we only have DeviceImageModel, we'll just skip creating anything in DB for now
            # but return the names in the response if we had a way to map them.
            pass

        camera_responses.append(
            ProvisionCameraResponse(
                local_name=cam_name,
                camera_id=uuid.uuid4(),  # Placeholder
            )
        )

    db.commit()

    return ProvisionResponse(
        device_id=device.id,
        sensors=sensor_responses,
        cameras=camera_responses,
    )
