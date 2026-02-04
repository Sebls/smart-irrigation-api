import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.devices import TelemetryRequest, TelemetryResponse
from app.api.services import devices_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/devices", tags=["devices"])


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
