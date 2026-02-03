from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base
from app.infrastructure.models._mixins import UUIDPrimaryKeyMixin


class ActivityEventModel(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "activity_events"

    zone_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    plant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("plants.id"), nullable=True)
    sensor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sensors.id"), nullable=True)

    type: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    zone: Mapped["ZoneModel | None"] = relationship(back_populates="activity_events")
    plant: Mapped["PlantModel | None"] = relationship(back_populates="activity_events")
    sensor: Mapped["SensorModel | None"] = relationship(back_populates="activity_events")

    __table_args__ = (
        Index("idx_activity_zone_time", "zone_id", "occurred_at"),
        Index("idx_activity_plant_time", "plant_id", "occurred_at"),
        Index("idx_activity_sensor_time", "sensor_id", "occurred_at"),
        Index("idx_activity_type", "type"),
    )

