from __future__ import annotations

from datetime import date, datetime
import uuid

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base
from app.infrastructure.models._mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WaterTank(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "water_tanks"

    name: Mapped[str] = mapped_column(String, nullable=False)
    capacity_liters: Mapped[int] = mapped_column(Integer, nullable=False)

    readings: Mapped[list["WaterTankReading"]] = relationship(back_populates="tank")
    consumption_daily: Mapped[list["WaterConsumptionDaily"]] = relationship(back_populates="tank")
    usage_hourly: Mapped[list["WaterUsageHourly"]] = relationship(back_populates="tank")

    __table_args__ = (Index("idx_water_tanks_deleted_at", "deleted_at"),)


class WaterTankReading(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "water_tank_readings"

    tank_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("water_tanks.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    level_percent: Mapped[object] = mapped_column(Numeric(5, 2), nullable=False)
    current_liters: Mapped[object] = mapped_column(Numeric(12, 2), nullable=False)

    tank: Mapped["WaterTank"] = relationship(back_populates="readings")

    __table_args__ = (
        CheckConstraint("level_percent >= 0 and level_percent <= 100", name="ck_water_tank_level_percent"),
        UniqueConstraint("tank_id", "recorded_at", name="uq_tank_readings_tank_time"),
        Index("idx_tank_readings_tank_time", "tank_id", "recorded_at"),
    )


class WaterConsumptionDaily(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "water_consumption_daily"

    tank_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("water_tanks.id"), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    amount_liters: Mapped[object] = mapped_column(Numeric(12, 2), nullable=False)

    tank: Mapped["WaterTank"] = relationship(back_populates="consumption_daily")

    __table_args__ = (
        CheckConstraint("amount_liters >= 0", name="ck_consumption_amount_nonnegative"),
        UniqueConstraint("tank_id", "day", name="uq_consumption_tank_day"),
        Index("idx_consumption_tank_day", "tank_id", "day"),
    )


class WaterUsageHourly(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "water_usage_hourly"

    tank_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("water_tanks.id"), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    usage_liters: Mapped[object] = mapped_column(Numeric(12, 2), nullable=False)

    tank: Mapped["WaterTank"] = relationship(back_populates="usage_hourly")

    __table_args__ = (
        CheckConstraint("hour >= 0 and hour <= 23", name="ck_usage_hour_range"),
        CheckConstraint("usage_liters >= 0", name="ck_usage_liters_nonnegative"),
        UniqueConstraint("tank_id", "day", "hour", name="uq_usage_hourly_tank_day_hour"),
        Index("idx_usage_hourly_tank_day", "tank_id", "day"),
    )


class ZoneWaterUsageDaily(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "zone_water_usage_daily"

    zone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("zones.id"), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    water_usage_liters: Mapped[object] = mapped_column(Numeric(12, 2), nullable=False)

    zone: Mapped["Zone"] = relationship(back_populates="zone_water_usage_daily")

    __table_args__ = (
        CheckConstraint("water_usage_liters >= 0", name="ck_zone_water_usage_nonnegative"),
        UniqueConstraint("zone_id", "day", name="uq_zone_water_usage_zone_day"),
        Index("idx_zone_water_usage_day", "day"),
        Index("idx_zone_water_usage_zone_day", "zone_id", "day"),
    )

