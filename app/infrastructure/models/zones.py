from __future__ import annotations

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.models._mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Zone(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "zones"

    name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")

    plants: Mapped[list["Plant"]] = relationship(back_populates="zone")
    sensors: Mapped[list["Sensor"]] = relationship(back_populates="zone")
    irrigation_jobs: Mapped[list["IrrigationJob"]] = relationship(back_populates="zone")
    activity_events: Mapped[list["ActivityEvent"]] = relationship(back_populates="zone")
    zone_water_usage_daily: Mapped[list["ZoneWaterUsageDaily"]] = relationship(back_populates="zone")

    __table_args__ = (
        Index("idx_zones_active", "is_active"),
        Index("idx_zones_deleted_at", "deleted_at"),
        # Optional uniqueness for name (per docs). Commented out until desired:
        # UniqueConstraint("name", name="uq_zones_name"),
    )

