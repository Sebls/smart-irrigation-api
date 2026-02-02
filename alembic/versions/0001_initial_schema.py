"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-02-02
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "zones",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_zones_active", "zones", ["is_active"])
    op.create_index("idx_zones_deleted_at", "zones", ["deleted_at"])

    op.create_table(
        "plants",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("zone_id", sa.Uuid(), sa.ForeignKey("zones.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("health", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("health in ('excellent','good','needs-attention','critical')", name="ck_plants_health"),
    )
    op.create_index("idx_plants_zone_id", "plants", ["zone_id"])
    op.create_index("idx_plants_deleted_at", "plants", ["deleted_at"])

    op.create_table(
        "sensors",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("plant_id", sa.Uuid(), sa.ForeignKey("plants.id"), nullable=True),
        sa.Column("zone_id", sa.Uuid(), sa.ForeignKey("zones.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("type in ('humidity','temperature','air-quality')", name="ck_sensors_type"),
        sa.CheckConstraint(
            "((plant_id is not null) + (zone_id is not null)) = 1",
            name="ck_sensors_exactly_one_parent",
        ),
    )
    op.create_index("idx_sensors_plant_id", "sensors", ["plant_id"])
    op.create_index("idx_sensors_zone_id", "sensors", ["zone_id"])
    op.create_index("idx_sensors_type", "sensors", ["type"])
    op.create_index("idx_sensors_deleted_at", "sensors", ["deleted_at"])

    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("sensor_id", sa.Uuid(), sa.ForeignKey("sensors.id"), nullable=False),
        sa.Column(
            "recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("value", sa.Float(), nullable=False),
        sa.UniqueConstraint("sensor_id", "recorded_at", name="uq_sensor_readings_sensor_time"),
    )
    op.create_index("idx_sensor_readings_sensor_time", "sensor_readings", ["sensor_id", "recorded_at"])

    op.create_table(
        "water_tanks",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("capacity_liters", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_water_tanks_deleted_at", "water_tanks", ["deleted_at"])

    op.create_table(
        "water_tank_readings",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("tank_id", sa.Uuid(), sa.ForeignKey("water_tanks.id"), nullable=False),
        sa.Column(
            "recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("level_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("current_liters", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("level_percent >= 0 and level_percent <= 100", name="ck_water_tank_level_percent"),
        sa.UniqueConstraint("tank_id", "recorded_at", name="uq_tank_readings_tank_time"),
    )
    op.create_index("idx_tank_readings_tank_time", "water_tank_readings", ["tank_id", "recorded_at"])

    op.create_table(
        "water_consumption_daily",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("tank_id", sa.Uuid(), sa.ForeignKey("water_tanks.id"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("amount_liters", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("amount_liters >= 0", name="ck_consumption_amount_nonnegative"),
        sa.UniqueConstraint("tank_id", "day", name="uq_consumption_tank_day"),
    )
    op.create_index("idx_consumption_tank_day", "water_consumption_daily", ["tank_id", "day"])

    op.create_table(
        "water_usage_hourly",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("tank_id", sa.Uuid(), sa.ForeignKey("water_tanks.id"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("usage_liters", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("hour >= 0 and hour <= 23", name="ck_usage_hour_range"),
        sa.CheckConstraint("usage_liters >= 0", name="ck_usage_liters_nonnegative"),
        sa.UniqueConstraint("tank_id", "day", "hour", name="uq_usage_hourly_tank_day_hour"),
    )
    op.create_index("idx_usage_hourly_tank_day", "water_usage_hourly", ["tank_id", "day"])

    op.create_table(
        "zone_water_usage_daily",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("zone_id", sa.Uuid(), sa.ForeignKey("zones.id"), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("water_usage_liters", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("water_usage_liters >= 0", name="ck_zone_water_usage_nonnegative"),
        sa.UniqueConstraint("zone_id", "day", name="uq_zone_water_usage_zone_day"),
    )
    op.create_index("idx_zone_water_usage_day", "zone_water_usage_daily", ["day"])
    op.create_index("idx_zone_water_usage_zone_day", "zone_water_usage_daily", ["zone_id", "day"])

    op.create_table(
        "irrigation_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("scope", sa.String(), nullable=False),
        sa.Column("zone_id", sa.Uuid(), sa.ForeignKey("zones.id"), nullable=True),
        sa.Column("plant_id", sa.Uuid(), sa.ForeignKey("plants.id"), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.CheckConstraint("scope in ('zone','plant')", name="ck_irrigation_jobs_scope"),
        sa.CheckConstraint("action in ('start','stop')", name="ck_irrigation_jobs_action"),
        sa.CheckConstraint(
            "status in ('accepted','running','completed','failed','cancelled')",
            name="ck_irrigation_jobs_status",
        ),
        sa.CheckConstraint(
            "duration_seconds is null or duration_seconds > 0",
            name="ck_irrigation_jobs_duration_positive",
        ),
        sa.CheckConstraint(
            "((zone_id is not null) + (plant_id is not null)) = 1",
            name="ck_irrigation_jobs_exactly_one_parent",
        ),
    )
    op.create_index("idx_irrigation_jobs_zone", "irrigation_jobs", ["zone_id", "requested_at"])
    op.create_index("idx_irrigation_jobs_plant", "irrigation_jobs", ["plant_id", "requested_at"])
    op.create_index("idx_irrigation_jobs_status", "irrigation_jobs", ["status"])

    op.create_table(
        "activity_events",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("zone_id", sa.Uuid(), sa.ForeignKey("zones.id"), nullable=True),
        sa.Column("plant_id", sa.Uuid(), sa.ForeignKey("plants.id"), nullable=True),
        sa.Column("sensor_id", sa.Uuid(), sa.ForeignKey("sensors.id"), nullable=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("idx_activity_zone_time", "activity_events", ["zone_id", "occurred_at"])
    op.create_index("idx_activity_plant_time", "activity_events", ["plant_id", "occurred_at"])
    op.create_index("idx_activity_sensor_time", "activity_events", ["sensor_id", "occurred_at"])
    op.create_index("idx_activity_type", "activity_events", ["type"])


def downgrade() -> None:
    op.drop_index("idx_activity_type", table_name="activity_events")
    op.drop_index("idx_activity_sensor_time", table_name="activity_events")
    op.drop_index("idx_activity_plant_time", table_name="activity_events")
    op.drop_index("idx_activity_zone_time", table_name="activity_events")
    op.drop_table("activity_events")

    op.drop_index("idx_irrigation_jobs_status", table_name="irrigation_jobs")
    op.drop_index("idx_irrigation_jobs_plant", table_name="irrigation_jobs")
    op.drop_index("idx_irrigation_jobs_zone", table_name="irrigation_jobs")
    op.drop_table("irrigation_jobs")

    op.drop_index("idx_zone_water_usage_zone_day", table_name="zone_water_usage_daily")
    op.drop_index("idx_zone_water_usage_day", table_name="zone_water_usage_daily")
    op.drop_table("zone_water_usage_daily")

    op.drop_index("idx_usage_hourly_tank_day", table_name="water_usage_hourly")
    op.drop_table("water_usage_hourly")

    op.drop_index("idx_consumption_tank_day", table_name="water_consumption_daily")
    op.drop_table("water_consumption_daily")

    op.drop_index("idx_tank_readings_tank_time", table_name="water_tank_readings")
    op.drop_table("water_tank_readings")

    op.drop_index("idx_water_tanks_deleted_at", table_name="water_tanks")
    op.drop_table("water_tanks")

    op.drop_index("idx_sensor_readings_sensor_time", table_name="sensor_readings")
    op.drop_table("sensor_readings")

    op.drop_index("idx_sensors_deleted_at", table_name="sensors")
    op.drop_index("idx_sensors_type", table_name="sensors")
    op.drop_index("idx_sensors_zone_id", table_name="sensors")
    op.drop_index("idx_sensors_plant_id", table_name="sensors")
    op.drop_table("sensors")

    op.drop_index("idx_plants_deleted_at", table_name="plants")
    op.drop_index("idx_plants_zone_id", table_name="plants")
    op.drop_table("plants")

    op.drop_index("idx_zones_deleted_at", table_name="zones")
    op.drop_index("idx_zones_active", table_name="zones")
    op.drop_table("zones")

