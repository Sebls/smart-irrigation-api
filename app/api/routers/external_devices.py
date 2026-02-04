import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.devices import (
    TelemetryRequest,
    TelemetryResponse,
    DeviceLogCreate,
    DeviceLogResponse,
    DeviceImageCreate,
    DeviceImageResponse,
    DeviceStatusResponse,
)
from app.api.services import devices_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/external-devices", tags=["external-devices"])


@router.post(
    "/{device_id}/telemetry",
    response_model=TelemetryResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_telemetry(
    device_id: uuid.UUID, request: TelemetryRequest, db: Session = Depends(get_db)
):
    try:
        return devices_service.save_telemetry(db, request, device_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{device_id}/images",
    response_model=DeviceImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_image(
    device_id: uuid.UUID, request: DeviceImageCreate, db: Session = Depends(get_db)
):
    try:
        return devices_service.save_image(db, device_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{device_id}/logs",
    response_model=DeviceLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_log(
    device_id: uuid.UUID, request: DeviceLogCreate, db: Session = Depends(get_db)
):
    try:
        return devices_service.save_log(db, device_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{device_id}/status",
    response_model=DeviceStatusResponse,
)
def get_device_status(device_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return devices_service.get_device_status(db, device_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
