import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.devices import (
    Device,
    DeviceCreate,
    DeviceUpdate,
)
from app.api.services import devices_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
def create_device_endpoint(device: DeviceCreate, db: Session = Depends(get_db)):
    try:
        return devices_service.create_device(db, device)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Device])
def list_devices_endpoint(db: Session = Depends(get_db)):
    return devices_service.get_devices(db)


@router.get("/{device_id}", response_model=Device)
def get_device_endpoint(device_id: uuid.UUID, db: Session = Depends(get_db)):
    db_device = devices_service.get_device(db, device_id)
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


@router.put("/{device_id}", response_model=Device)
def update_device_endpoint(
    device_id: uuid.UUID, device: DeviceUpdate, db: Session = Depends(get_db)
):
    db_device = devices_service.update_device(db, device_id, device)
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


@router.delete("/{device_id}", response_model=Device)
def delete_device_endpoint(device_id: uuid.UUID, db: Session = Depends(get_db)):
    db_device = devices_service.delete_device(db, device_id)
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device
