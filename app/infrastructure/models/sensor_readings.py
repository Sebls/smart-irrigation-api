from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from sqlalchemy.sql import func


class SensorReadingModel(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sensor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sensors.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    value: Mapped[float] = mapped_column(Float, nullable=False)

    sensor: Mapped["SensorModel"] = relationship(back_populates="readings")

    __table_args__ = (
        UniqueConstraint("sensor_id", "recorded_at", name="uq_sensor_readings_sensor_time"),
        Index("idx_sensor_readings_sensor_time", "sensor_id", "recorded_at"),
    )

