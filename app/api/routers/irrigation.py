from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.irrigation import (
    IrrigationJobCreate,
    IrrigationJobUpdate,
    IrrigationJob,
)
from app.api.services import irrigation_service
from app.api.dependencies import get_db

router = APIRouter(prefix="/irrigation", tags=["irrigation"])


@router.post("/", response_model=IrrigationJob, status_code=status.HTTP_201_CREATED)
def create_irrigation_job_endpoint(
    job: IrrigationJobCreate, db: Session = Depends(get_db)
):
    try:
        return irrigation_service.create_irrigation_job(db, job)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[IrrigationJob])
def list_irrigation_jobs_endpoint(
    status: Optional[str] = None,
    zone_id: Optional[str] = None,
    plant_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return irrigation_service.get_irrigation_jobs(
        db, status=status, zone_id=zone_id, plant_id=plant_id, skip=skip, limit=limit
    )


@router.get("/{job_id}", response_model=IrrigationJob)
def get_irrigation_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    db_job = irrigation_service.get_irrigation_job(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Irrigation job not found")
    return db_job


@router.put("/{job_id}", response_model=IrrigationJob)
def update_irrigation_job_endpoint(
    job_id: str, job: IrrigationJobUpdate, db: Session = Depends(get_db)
):
    db_job = irrigation_service.update_irrigation_job(db, job_id, job)
    if not db_job:
        raise HTTPException(status_code=404, detail="Irrigation job not found")
    return db_job


@router.delete("/{job_id}", response_model=IrrigationJob)
def delete_irrigation_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    db_job = irrigation_service.delete_irrigation_job(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Irrigation job not found")
    return db_job
