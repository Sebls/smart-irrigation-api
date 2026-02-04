from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.sensor_readings import SensorReadingCreate, SensorReading
from app.api.services import sensor_readings_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/sensor-readings", tags=["sensor-readings"])


@router.post("/", response_model=SensorReading, status_code=status.HTTP_201_CREATED)
def create_sensor_reading_endpoint(
    reading: SensorReadingCreate, db: Session = Depends(get_db)
):
    try:
        return sensor_readings_service.create_sensor_reading(db, reading)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[SensorReading])
def list_sensor_readings_endpoint(
    sensor_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return sensor_readings_service.get_sensor_readings(
        db, sensor_id=sensor_id, skip=skip, limit=limit
    )


@router.get("/{reading_id}", response_model=SensorReading)
def get_sensor_reading_endpoint(reading_id: str, db: Session = Depends(get_db)):
    db_reading = sensor_readings_service.get_sensor_reading(db, reading_id)
    if not db_reading:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    return db_reading


@router.delete("/{reading_id}", response_model=SensorReading)
def delete_sensor_reading_endpoint(reading_id: str, db: Session = Depends(get_db)):
    db_reading = sensor_readings_service.delete_sensor_reading(db, reading_id)
    if not db_reading:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    return db_reading
