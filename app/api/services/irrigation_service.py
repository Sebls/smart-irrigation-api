from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from app.infrastructure.models.irrigation import IrrigationJobModel
from app.api.schemas.irrigation import (
    IrrigationJobCreate,
    IrrigationJobUpdate,
    IrrigationJob,
)


def create_irrigation_job(db: Session, job: IrrigationJobCreate) -> IrrigationJob:
    zone_uuid = uuid.UUID(job.zone_id) if job.zone_id else None
    plant_uuid = uuid.UUID(job.plant_id) if job.plant_id else None

    db_job = IrrigationJobModel(
        scope=job.scope,
        zone_id=zone_uuid,
        plant_id=plant_uuid,
        action=job.action,
        duration_seconds=job.duration_seconds,
        status=job.status,
    )
    db.add(db_job)
    try:
        db.commit()
        db.refresh(db_job)
        return IrrigationJob.model_validate(db_job)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise e


def get_irrigation_jobs(
    db: Session,
    status: Optional[str] = None,
    zone_id: Optional[str] = None,
    plant_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[IrrigationJob]:
    query = db.query(IrrigationJobModel)
    if status:
        query = query.filter(IrrigationJobModel.status == status)
    if zone_id:
        try:
            query = query.filter(IrrigationJobModel.zone_id == uuid.UUID(zone_id))
        except ValueError:
            pass
    if plant_id:
        try:
            query = query.filter(IrrigationJobModel.plant_id == uuid.UUID(plant_id))
        except ValueError:
            pass

    db_jobs = (
        query.order_by(IrrigationJobModel.requested_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [IrrigationJob.model_validate(job) for job in db_jobs]


def get_irrigation_job(db: Session, job_id: str) -> Optional[IrrigationJob]:
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        return None

    db_job = (
        db.query(IrrigationJobModel).filter(IrrigationJobModel.id == job_uuid).first()
    )
    if not db_job:
        return None
    return IrrigationJob.model_validate(db_job)


def update_irrigation_job(
    db: Session, job_id: str, job: IrrigationJobUpdate
) -> Optional[IrrigationJob]:
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        return None

    db_job = (
        db.query(IrrigationJobModel).filter(IrrigationJobModel.id == job_uuid).first()
    )
    if not db_job:
        return None

    data = job.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_job, key, value)

    try:
        db.commit()
        db.refresh(db_job)
        return IrrigationJob.model_validate(db_job)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Database integrity error: {str(e.orig)}")


def delete_irrigation_job(db: Session, job_id: str) -> Optional[IrrigationJob]:
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        return None

    db_job = (
        db.query(IrrigationJobModel).filter(IrrigationJobModel.id == job_uuid).first()
    )
    if not db_job:
        return None

    db.delete(db_job)
    db.commit()
    return IrrigationJob.model_validate(db_job)
