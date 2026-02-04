from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.infrastructure.models.water import WaterTankModel, WaterTankReadingModel
from app.api.schemas.water import (
    WaterTankCreate,
    WaterTankUpdate,
    WaterTank,
    WaterTankReadingCreate,
    WaterTankReading,
)


# Tank Services
def create_tank(db: Session, tank: WaterTankCreate) -> WaterTank:
    db_tank = WaterTankModel(
        name=tank.name,
        capacity_liters=tank.capacity_liters,
    )
    db.add(db_tank)
    try:
        db.commit()
        db.refresh(db_tank)
        return WaterTank.model_validate(db_tank)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_tanks(db: Session, skip: int = 0, limit: int = 100) -> List[WaterTank]:
    db_tanks = (
        db.query(WaterTankModel)
        .filter(WaterTankModel.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [WaterTank.model_validate(tank) for tank in db_tanks]


def get_tank(db: Session, tank_id: str) -> Optional[WaterTank]:
    try:
        tank_uuid = uuid.UUID(tank_id)
    except ValueError:
        return None

    db_tank = (
        db.query(WaterTankModel)
        .filter(WaterTankModel.id == tank_uuid, WaterTankModel.deleted_at.is_(None))
        .first()
    )
    if not db_tank:
        return None
    return WaterTank.model_validate(db_tank)


def update_tank(
    db: Session, tank_id: str, tank: WaterTankUpdate
) -> Optional[WaterTank]:
    try:
        tank_uuid = uuid.UUID(tank_id)
    except ValueError:
        return None

    db_tank = (
        db.query(WaterTankModel)
        .filter(WaterTankModel.id == tank_uuid, WaterTankModel.deleted_at.is_(None))
        .first()
    )
    if not db_tank:
        return None

    data = tank.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_tank, key, value)

    try:
        db.commit()
        db.refresh(db_tank)
        return WaterTank.model_validate(db_tank)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")


def delete_tank(db: Session, tank_id: str) -> Optional[WaterTank]:
    try:
        tank_uuid = uuid.UUID(tank_id)
    except ValueError:
        return None

    db_tank = (
        db.query(WaterTankModel)
        .filter(WaterTankModel.id == tank_uuid, WaterTankModel.deleted_at.is_(None))
        .first()
    )
    if not db_tank:
        return None

    # Soft delete
    from datetime import datetime

    db_tank.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_tank)
    return WaterTank.model_validate(db_tank)


# Reading Services
def create_tank_reading(
    db: Session, reading: WaterTankReadingCreate
) -> WaterTankReading:
    tank_uuid = uuid.UUID(reading.tank_id)
    db_reading = WaterTankReadingModel(
        tank_id=tank_uuid,
        level_percent=reading.level_percent,
        current_liters=reading.current_liters,
        recorded_at=reading.recorded_at,
    )
    db.add(db_reading)
    try:
        db.commit()
        db.refresh(db_reading)
        return WaterTankReading.model_validate(db_reading)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_tank_readings(
    db: Session, tank_id: Optional[str] = None, skip: int = 0, limit: int = 100
) -> List[WaterTankReading]:
    query = db.query(WaterTankReadingModel)
    if tank_id:
        try:
            tank_uuid = uuid.UUID(tank_id)
            query = query.filter(WaterTankReadingModel.tank_id == tank_uuid)
        except ValueError:
            return []

    db_readings = (
        query.order_by(WaterTankReadingModel.recorded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [WaterTankReading.model_validate(reading) for reading in db_readings]


def get_tank_reading(db: Session, reading_id: str) -> Optional[WaterTankReading]:
    try:
        reading_uuid = uuid.UUID(reading_id)
    except ValueError:
        return None

    db_reading = (
        db.query(WaterTankReadingModel)
        .filter(WaterTankReadingModel.id == reading_uuid)
        .first()
    )
    if not db_reading:
        return None
    return WaterTankReading.model_validate(db_reading)


def delete_tank_reading(db: Session, reading_id: str) -> Optional[WaterTankReading]:
    try:
        reading_uuid = uuid.UUID(reading_id)
    except ValueError:
        return None

    db_reading = (
        db.query(WaterTankReadingModel)
        .filter(WaterTankReadingModel.id == reading_uuid)
        .first()
    )
    if not db_reading:
        return None

    db.delete(db_reading)
    db.commit()
    return WaterTankReading.model_validate(db_reading)
