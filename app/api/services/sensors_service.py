from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.infrastructure.models.sensors import SensorModel
from app.api.schemas.sensors import SensorCreate, SensorUpdate, Sensor


def create_sensor(db: Session, sensor: SensorCreate) -> Sensor:
    plant_uuid = uuid.UUID(sensor.plant_id) if sensor.plant_id else None
    zone_uuid = uuid.UUID(sensor.zone_id) if sensor.zone_id else None

    db_sensor = SensorModel(
        name=sensor.name,
        type=sensor.type,
        unit=sensor.unit,
        is_active=sensor.is_active,
        plant_id=plant_uuid,
        zone_id=zone_uuid,
    )
    db.add(db_sensor)
    try:
        db.commit()
        db.refresh(db_sensor)
        return Sensor.model_validate(db_sensor)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_sensors(db: Session, skip: int = 0, limit: int = 100) -> List[Sensor]:
    db_sensors = (
        db.query(SensorModel)
        .filter(SensorModel.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [Sensor.model_validate(sensor) for sensor in db_sensors]


def get_sensor(db: Session, sensor_id: str) -> Optional[Sensor]:
    try:
        sensor_uuid = uuid.UUID(sensor_id)
    except ValueError:
        return None

    db_sensor = (
        db.query(SensorModel)
        .filter(SensorModel.id == sensor_uuid, SensorModel.deleted_at.is_(None))
        .first()
    )
    if not db_sensor:
        return None
    return Sensor.model_validate(db_sensor)


def update_sensor(
    db: Session, sensor_id: str, sensor: SensorUpdate
) -> Optional[Sensor]:
    try:
        sensor_uuid = uuid.UUID(sensor_id)
    except ValueError:
        return None

    db_sensor = (
        db.query(SensorModel)
        .filter(SensorModel.id == sensor_uuid, SensorModel.deleted_at.is_(None))
        .first()
    )
    if not db_sensor:
        return None

    data = sensor.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key in ["plant_id", "zone_id"] and value is not None:
            setattr(db_sensor, key, uuid.UUID(value))
        else:
            setattr(db_sensor, key, value)

    try:
        db.commit()
        db.refresh(db_sensor)
        return Sensor.model_validate(db_sensor)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")


def delete_sensor(db: Session, sensor_id: str) -> Optional[Sensor]:
    try:
        sensor_uuid = uuid.UUID(sensor_id)
    except ValueError:
        return None

    db_sensor = (
        db.query(SensorModel)
        .filter(SensorModel.id == sensor_uuid, SensorModel.deleted_at.is_(None))
        .first()
    )
    if not db_sensor:
        return None

    # Soft delete
    from datetime import datetime

    db_sensor.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_sensor)
    return Sensor.model_validate(db_sensor)
