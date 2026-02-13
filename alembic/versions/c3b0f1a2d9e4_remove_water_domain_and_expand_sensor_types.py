"""remove water domain and expand sensor types

Revision ID: c3b0f1a2d9e4
Revises: a61f47297566
Create Date: 2026-02-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "c3b0f1a2d9e4"
down_revision = "a61f47297566"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    # Drop water-related tables (no longer part of domain).
    # Order matters due to FK dependencies.
    for table in [
        "water_consumption_daily",
        "water_usage_hourly",
        "water_tank_readings",
        "water_tanks",
        "zone_water_usage_daily",
    ]:
        if table in tables:
            op.drop_table(table)

    # Expand supported sensor types to match current domain model.
    # Original constraint only allowed: humidity, temperature, air-quality
    if "sensors" in tables:
        with op.batch_alter_table("sensors", schema=None) as batch_op:
            batch_op.drop_constraint("ck_sensors_type", type_="check")
            batch_op.create_check_constraint(
                "ck_sensors_type",
                "type in ('humidity','temperature','air-quality','water-level','flow')",
            )


def downgrade() -> None:
    # Revert sensor types constraint.
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "sensors" in tables:
        with op.batch_alter_table("sensors", schema=None) as batch_op:
            batch_op.drop_constraint("ck_sensors_type", type_="check")
            batch_op.create_check_constraint(
                "ck_sensors_type",
                "type in ('humidity','temperature','air-quality')",
            )

    # Recreate removed water tables (minimal schema to match 0001).
    if "water_tanks" not in tables:
        op.create_table(
            "water_tanks",
            sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("capacity_liters", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("idx_water_tanks_deleted_at", "water_tanks", ["deleted_at"])

    if "water_tank_readings" not in tables:
        op.create_table(
            "water_tank_readings",
            sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
            sa.Column("tank_id", sa.Uuid(), sa.ForeignKey("water_tanks.id"), nullable=False),
            sa.Column(
                "recorded_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("level_percent", sa.Numeric(5, 2), nullable=False),
            sa.Column("current_liters", sa.Numeric(12, 2), nullable=False),
            sa.CheckConstraint("level_percent >= 0 and level_percent <= 100", name="ck_water_tank_level_percent"),
            sa.UniqueConstraint("tank_id", "recorded_at", name="uq_tank_readings_tank_time"),
        )
        op.create_index("idx_tank_readings_tank_time", "water_tank_readings", ["tank_id", "recorded_at"])

    if "water_consumption_daily" not in tables:
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

    if "water_usage_hourly" not in tables:
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

    if "zone_water_usage_daily" not in tables:
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
        op.create_index(
            "idx_zone_water_usage_zone_day", "zone_water_usage_daily", ["zone_id", "day"]
        )

