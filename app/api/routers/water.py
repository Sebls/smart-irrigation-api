from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.water import (
    WaterTankCreate,
    WaterTankUpdate,
    WaterTank,
    WaterTankReadingCreate,
    WaterTankReading,
)
from app.api.services import water_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/water", tags=["water"])


# Tank Endpoints
@router.post("/tanks/", response_model=WaterTank, status_code=status.HTTP_201_CREATED)
def create_tank_endpoint(tank: WaterTankCreate, db: Session = Depends(get_db)):
    try:
        return water_service.create_tank(db, tank)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tanks/", response_model=List[WaterTank])
def list_tanks_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return water_service.get_tanks(db, skip=skip, limit=limit)


@router.get("/tanks/{tank_id}", response_model=WaterTank)
def get_tank_endpoint(tank_id: str, db: Session = Depends(get_db)):
    db_tank = water_service.get_tank(db, tank_id)
    if not db_tank:
        raise HTTPException(status_code=404, detail="Water tank not found")
    return db_tank


@router.put("/tanks/{tank_id}", response_model=WaterTank)
def update_tank_endpoint(
    tank_id: str, tank: WaterTankUpdate, db: Session = Depends(get_db)
):
    db_tank = water_service.update_tank(db, tank_id, tank)
    if not db_tank:
        raise HTTPException(status_code=404, detail="Water tank not found")
    return db_tank


@router.delete("/tanks/{tank_id}", response_model=WaterTank)
def delete_tank_endpoint(tank_id: str, db: Session = Depends(get_db)):
    db_tank = water_service.delete_tank(db, tank_id)
    if not db_tank:
        raise HTTPException(status_code=404, detail="Water tank not found")
    return db_tank


# Reading Endpoints
@router.post(
    "/readings/", response_model=WaterTankReading, status_code=status.HTTP_201_CREATED
)
def create_tank_reading_endpoint(
    reading: WaterTankReadingCreate, db: Session = Depends(get_db)
):
    try:
        return water_service.create_tank_reading(db, reading)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/readings/", response_model=List[WaterTankReading])
def list_tank_readings_endpoint(
    tank_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return water_service.get_tank_readings(db, tank_id=tank_id, skip=skip, limit=limit)


@router.get("/readings/{reading_id}", response_model=WaterTankReading)
def get_tank_reading_endpoint(reading_id: str, db: Session = Depends(get_db)):
    db_reading = water_service.get_tank_reading(db, reading_id)
    if not db_reading:
        raise HTTPException(status_code=404, detail="Water tank reading not found")
    return db_reading


@router.delete("/readings/{reading_id}", response_model=WaterTankReading)
def delete_tank_reading_endpoint(reading_id: str, db: Session = Depends(get_db)):
    db_reading = water_service.delete_tank_reading(db, reading_id)
    if not db_reading:
        raise HTTPException(status_code=404, detail="Water tank reading not found")
    return db_reading
