from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.infrastructure.models.activity import ActivityEventModel
from app.api.schemas.activity import ActivityEventCreate, ActivityEvent


def create_activity_event(db: Session, event: ActivityEventCreate) -> ActivityEvent:
    zone_uuid = uuid.UUID(event.zone_id) if event.zone_id else None
    plant_uuid = uuid.UUID(event.plant_id) if event.plant_id else None
    sensor_uuid = uuid.UUID(event.sensor_id) if event.sensor_id else None

    db_event = ActivityEventModel(
        type=event.type,
        message=event.message,
        zone_id=zone_uuid,
        plant_id=plant_uuid,
        sensor_id=sensor_uuid,
        occurred_at=event.occurred_at,
    )
    db.add(db_event)
    try:
        db.commit()
        db.refresh(db_event)
        return ActivityEvent.model_validate(db_event)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_activity_events(
    db: Session,
    type: Optional[str] = None,
    zone_id: Optional[str] = None,
    plant_id: Optional[str] = None,
    sensor_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[ActivityEvent]:
    query = db.query(ActivityEventModel)
    if type:
        query = query.filter(ActivityEventModel.type == type)
    if zone_id:
        try:
            query = query.filter(ActivityEventModel.zone_id == uuid.UUID(zone_id))
        except ValueError:
            pass
    if plant_id:
        try:
            query = query.filter(ActivityEventModel.plant_id == uuid.UUID(plant_id))
        except ValueError:
            pass
    if sensor_id:
        try:
            query = query.filter(ActivityEventModel.sensor_id == uuid.UUID(sensor_id))
        except ValueError:
            pass

    db_events = (
        query.order_by(ActivityEventModel.occurred_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [ActivityEvent.model_validate(event) for event in db_events]


def get_activity_event(db: Session, event_id: str) -> Optional[ActivityEvent]:
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        return None

    db_event = (
        db.query(ActivityEventModel).filter(ActivityEventModel.id == event_uuid).first()
    )
    if not db_event:
        return None
    return ActivityEvent.model_validate(db_event)


def delete_activity_event(db: Session, event_id: str) -> Optional[ActivityEvent]:
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        return None

    db_event = (
        db.query(ActivityEventModel).filter(ActivityEventModel.id == event_uuid).first()
    )
    if not db_event:
        return None

    db.delete(db_event)
    db.commit()
    return ActivityEvent.model_validate(db_event)
