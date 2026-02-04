from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.zones import ZoneCreate, ZoneUpdate, Zone
from app.api.services import zones_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/zones", tags=["zones"])


@router.post("/", response_model=Zone, status_code=status.HTTP_201_CREATED)
def create_zone_endpoint(zone: ZoneCreate, db: Session = Depends(get_db)):
    try:
        return zones_service.create_zone(db, zone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Zone])
def list_zones_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return zones_service.get_zones(db, skip=skip, limit=limit)


@router.get("/{zone_id}", response_model=Zone)
def get_zone_endpoint(zone_id: str, db: Session = Depends(get_db)):
    db_zone = zones_service.get_zone(db, zone_id)
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone


@router.put("/{zone_id}", response_model=Zone)
def update_zone_endpoint(zone_id: str, zone: ZoneUpdate, db: Session = Depends(get_db)):
    db_zone = zones_service.update_zone(db, zone_id, zone)
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone


@router.delete("/{zone_id}", response_model=Zone)
def delete_zone_endpoint(zone_id: str, db: Session = Depends(get_db)):
    db_zone = zones_service.delete_zone(db, zone_id)
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone
