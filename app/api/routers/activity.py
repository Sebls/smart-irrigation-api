from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.activity import ActivityEventCreate, ActivityEvent
from app.api.services import activity_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/", response_model=ActivityEvent, status_code=status.HTTP_201_CREATED)
def create_activity_event_endpoint(
    event: ActivityEventCreate, db: Session = Depends(get_db)
):
    try:
        return activity_service.create_activity_event(db, event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ActivityEvent])
def list_activity_events_endpoint(
    type: Optional[str] = None,
    zone_id: Optional[str] = None,
    plant_id: Optional[str] = None,
    sensor_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return activity_service.get_activity_events(
        db,
        type=type,
        zone_id=zone_id,
        plant_id=plant_id,
        sensor_id=sensor_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{event_id}", response_model=ActivityEvent)
def get_activity_event_endpoint(event_id: str, db: Session = Depends(get_db)):
    db_event = activity_service.get_activity_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Activity event not found")
    return db_event


@router.delete("/{event_id}", response_model=ActivityEvent)
def delete_activity_event_endpoint(event_id: str, db: Session = Depends(get_db)):
    db_event = activity_service.delete_activity_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Activity event not found")
    return db_event
