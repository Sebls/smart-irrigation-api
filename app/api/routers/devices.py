import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.schemas.devices import (
    Device,
    DeviceCreate,
    DeviceUpdate,
    ProvisionRequest,
    ProvisionResponse,
    DeviceImageResponse,
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


@router.post("/provision", response_model=ProvisionResponse)
def provision_device_endpoint(request: ProvisionRequest, db: Session = Depends(get_db)):
    try:
        return devices_service.provision_device(db, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{device_id}/images", response_model=List[DeviceImageResponse])
def list_device_images_endpoint(device_id: uuid.UUID, db: Session = Depends(get_db)):
    return devices_service.list_device_images(db, device_id)


@router.get("/{device_id}/images/{image_id}", response_model=DeviceImageResponse)
def get_device_image_endpoint(
    device_id: uuid.UUID, image_id: uuid.UUID, db: Session = Depends(get_db)
):
    img = devices_service.get_device_image(db, device_id, image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    return img


@router.get("/{device_id}/images/{image_id}/file")
def get_device_image_file_endpoint(
    device_id: uuid.UUID, image_id: uuid.UUID, db: Session = Depends(get_db)
):
    try:
        path, media_type, filename = devices_service.get_device_image_file(
            db, device_id, image_id
        )
        return FileResponse(path=path, media_type=media_type, filename=filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{device_id}/images/by-type/{image_type}/file")
def get_device_image_file_by_type_endpoint(
    device_id: uuid.UUID, image_type: str, db: Session = Depends(get_db)
):
    try:
        path, media_type, filename = devices_service.get_device_image_file_by_type(
            db, device_id, image_type
        )
        return FileResponse(path=path, media_type=media_type, filename=filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
