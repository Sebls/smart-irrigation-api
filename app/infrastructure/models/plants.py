from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.models._mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Plant(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "plants"

    zone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("zones.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    health: Mapped[str] = mapped_column(String, nullable=False)

    zone: Mapped["Zone"] = relationship(back_populates="plants")
    sensors: Mapped[list["Sensor"]] = relationship(back_populates="plant")
    irrigation_jobs: Mapped[list["IrrigationJob"]] = relationship(back_populates="plant")
    activity_events: Mapped[list["ActivityEvent"]] = relationship(back_populates="plant")

    __table_args__ = (
        CheckConstraint(
            "health in ('excellent','good','needs-attention','critical')",
            name="ck_plants_health",
        ),
        Index("idx_plants_zone_id", "zone_id"),
        Index("idx_plants_deleted_at", "deleted_at"),
        # Recommended uniqueness (per docs). Commented out until desired:
        # UniqueConstraint("zone_id", "name", name="uq_plants_zone_name"),
    )

