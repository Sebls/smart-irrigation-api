from __future__ import annotations

import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.models._mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class SensorModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sensors"

    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)

    plant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("plants.id"), nullable=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("zones.id"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

    plant: Mapped["PlantModel | None"] = relationship(back_populates="sensors")
    zone: Mapped["ZoneModel | None"] = relationship(back_populates="sensors")
    readings: Mapped[list["SensorReadingModel"]] = relationship(back_populates="sensor")
    activity_events: Mapped[list["ActivityEventModel"]] = relationship(
        back_populates="sensor"
    )

    __table_args__ = (
        CheckConstraint(
            "type in ('humidity','temperature','air-quality')", name="ck_sensors_type"
        ),
        # Exactly one parent: plant_id or zone_id
        CheckConstraint(
            "((plant_id is not null) + (zone_id is not null)) = 1",
            name="ck_sensors_exactly_one_parent",
        ),
        Index("idx_sensors_plant_id", "plant_id"),
        Index("idx_sensors_zone_id", "zone_id"),
        Index("idx_sensors_type", "type"),
        Index("idx_sensors_deleted_at", "deleted_at"),
    )
