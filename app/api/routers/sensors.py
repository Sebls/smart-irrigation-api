from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.sensors import SensorCreate, SensorUpdate, Sensor
from app.api.services import sensors_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post("/", response_model=Sensor, status_code=status.HTTP_201_CREATED)
def create_sensor_endpoint(sensor: SensorCreate, db: Session = Depends(get_db)):
    try:
        return sensors_service.create_sensor(db, sensor)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Sensor])
def list_sensors_endpoint(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return sensors_service.get_sensors(db, skip=skip, limit=limit)


@router.get("/{sensor_id}", response_model=Sensor)
def get_sensor_endpoint(sensor_id: str, db: Session = Depends(get_db)):
    db_sensor = sensors_service.get_sensor(db, sensor_id)
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return db_sensor


@router.put("/{sensor_id}", response_model=Sensor)
def update_sensor_endpoint(
    sensor_id: str, sensor: SensorUpdate, db: Session = Depends(get_db)
):
    db_sensor = sensors_service.update_sensor(db, sensor_id, sensor)
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return db_sensor


@router.delete("/{sensor_id}", response_model=Sensor)
def delete_sensor_endpoint(sensor_id: str, db: Session = Depends(get_db)):
    db_sensor = sensors_service.delete_sensor(db, sensor_id)
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return db_sensor
