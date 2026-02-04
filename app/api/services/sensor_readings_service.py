from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.infrastructure.models.sensor_readings import SensorReadingModel
from app.api.schemas.sensor_readings import SensorReadingCreate, SensorReading


def create_sensor_reading(db: Session, reading: SensorReadingCreate) -> SensorReading:
    sensor_uuid = uuid.UUID(reading.sensor_id)
    db_reading = SensorReadingModel(
        sensor_id=sensor_uuid,
        value=reading.value,
        recorded_at=reading.recorded_at,
    )
    db.add(db_reading)
    try:
        db.commit()
        db.refresh(db_reading)
        return SensorReading.model_validate(db_reading)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_sensor_readings(
    db: Session, sensor_id: Optional[str] = None, skip: int = 0, limit: int = 100
) -> List[SensorReading]:
    query = db.query(SensorReadingModel)
    if sensor_id:
        try:
            sensor_uuid = uuid.UUID(sensor_id)
            query = query.filter(SensorReadingModel.sensor_id == sensor_uuid)
        except ValueError:
            return []

    db_readings = (
        query.order_by(SensorReadingModel.recorded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [SensorReading.model_validate(reading) for reading in db_readings]


def get_sensor_reading(db: Session, reading_id: str) -> Optional[SensorReading]:
    try:
        reading_uuid = uuid.UUID(reading_id)
    except ValueError:
        return None

    db_reading = (
        db.query(SensorReadingModel)
        .filter(SensorReadingModel.id == reading_uuid)
        .first()
    )
    if not db_reading:
        return None
    return SensorReading.model_validate(db_reading)


# Note: Typical sensor readings are immutable, but implementing delete for CRUD completeness.
def delete_sensor_reading(db: Session, reading_id: str) -> Optional[SensorReading]:
    try:
        reading_uuid = uuid.UUID(reading_id)
    except ValueError:
        return None

    db_reading = (
        db.query(SensorReadingModel)
        .filter(SensorReadingModel.id == reading_uuid)
        .first()
    )
    if not db_reading:
        return None

    db.delete(db_reading)
    db.commit()
    return SensorReading.model_validate(db_reading)
