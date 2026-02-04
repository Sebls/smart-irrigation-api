from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.infrastructure.models.zones import ZoneModel
from app.api.schemas.zones import ZoneCreate, ZoneUpdate, Zone


def create_zone(db: Session, zone: ZoneCreate) -> Zone:
    db_zone = ZoneModel(
        name=zone.name,
        is_active=zone.is_active,
    )
    db.add(db_zone)
    try:
        db.commit()
        db.refresh(db_zone)
        return Zone.model_validate(db_zone)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_zones(db: Session, skip: int = 0, limit: int = 100) -> List[Zone]:
    db_zones = (
        db.query(ZoneModel)
        .filter(ZoneModel.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [Zone.model_validate(zone) for zone in db_zones]


def get_zone(db: Session, zone_id: str) -> Optional[Zone]:
    try:
        zone_uuid = uuid.UUID(zone_id)
    except ValueError:
        return None

    db_zone = (
        db.query(ZoneModel)
        .filter(ZoneModel.id == zone_uuid, ZoneModel.deleted_at.is_(None))
        .first()
    )
    if not db_zone:
        return None
    return Zone.model_validate(db_zone)


def update_zone(db: Session, zone_id: str, zone: ZoneUpdate) -> Optional[Zone]:
    try:
        zone_uuid = uuid.UUID(zone_id)
    except ValueError:
        return None

    db_zone = (
        db.query(ZoneModel)
        .filter(ZoneModel.id == zone_uuid, ZoneModel.deleted_at.is_(None))
        .first()
    )
    if not db_zone:
        return None

    data = zone.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_zone, key, value)

    try:
        db.commit()
        db.refresh(db_zone)
        return Zone.model_validate(db_zone)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")


def delete_zone(db: Session, zone_id: str) -> Optional[Zone]:
    try:
        zone_uuid = uuid.UUID(zone_id)
    except ValueError:
        return None

    db_zone = (
        db.query(ZoneModel)
        .filter(ZoneModel.id == zone_uuid, ZoneModel.deleted_at.is_(None))
        .first()
    )
    if not db_zone:
        return None

    # Soft delete
    from datetime import datetime

    db_zone.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(db_zone)
    return Zone.model_validate(db_zone)
