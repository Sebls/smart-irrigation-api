from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base
from app.infrastructure.models._mixins import UUIDPrimaryKeyMixin


class IrrigationJob(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "irrigation_jobs"

    scope: Mapped[str] = mapped_column(String, nullable=False)
    zone_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    plant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("plants.id"), nullable=True)

    action: Mapped[str] = mapped_column(String, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)

    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    zone: Mapped["Zone | None"] = relationship(back_populates="irrigation_jobs")
    plant: Mapped["Plant | None"] = relationship(back_populates="irrigation_jobs")

    __table_args__ = (
        CheckConstraint("scope in ('zone','plant')", name="ck_irrigation_jobs_scope"),
        CheckConstraint("action in ('start','stop')", name="ck_irrigation_jobs_action"),
        CheckConstraint(
            "status in ('accepted','running','completed','failed','cancelled')",
            name="ck_irrigation_jobs_status",
        ),
        CheckConstraint(
            "duration_seconds is null or duration_seconds > 0",
            name="ck_irrigation_jobs_duration_positive",
        ),
        CheckConstraint(
            "((zone_id is not null) + (plant_id is not null)) = 1",
            name="ck_irrigation_jobs_exactly_one_parent",
        ),
        Index("idx_irrigation_jobs_zone", "zone_id", "requested_at"),
        Index("idx_irrigation_jobs_plant", "plant_id", "requested_at"),
        Index("idx_irrigation_jobs_status", "status"),
    )

