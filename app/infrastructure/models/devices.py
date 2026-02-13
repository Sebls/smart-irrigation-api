from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.models._mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class DeviceModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "devices"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    hardware_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

    # Liveness and Health
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    uptime: Mapped[float | None] = mapped_column(Float, nullable=True)  # in seconds

    # Relationships
    logs: Mapped[list["DeviceLogModel"]] = relationship(back_populates="device")
    images: Mapped[list["DeviceImageModel"]] = relationship(back_populates="device")


class DeviceLogModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "device_logs"

    device_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("devices.id"), nullable=False
    )
    level: Mapped[str] = mapped_column(
        String, nullable=False
    )  # info, warning, error, critical
    message: Mapped[str] = mapped_column(String, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    device: Mapped["DeviceModel"] = relationship(back_populates="logs")

    __table_args__ = (
        Index("idx_device_logs_device_id", "device_id"),
        Index("idx_device_logs_level", "level"),
        Index("idx_device_logs_recorded_at", "recorded_at"),
    )


class DeviceImageModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "device_images"

    device_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("devices.id"), nullable=False
    )
    plant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("plants.id"), nullable=True
    )
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("zones.id"), nullable=True
    )

    image_url: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # plant, tank, zone
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    metadata_json: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # flexible extra info

    device: Mapped["DeviceModel"] = relationship(back_populates="images")

    __table_args__ = (
        Index("idx_device_images_device_id", "device_id"),
        Index("idx_device_images_plant_id", "plant_id"),
        Index("idx_device_images_zone_id", "zone_id"),
        Index("idx_device_images_captured_at", "captured_at"),
    )
