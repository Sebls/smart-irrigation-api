"""add hardware_id to devices

Revision ID: a61f47297566
Revises: 0001_initial_schema
Create Date: 2026-02-06 16:41:52.605626
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "a61f47297566"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Ensure devices tables exist; add hardware_id when needed.

    NOTE:
    Earlier revisions did not create the `devices` tables. This migration is
    intentionally defensive so a fresh `alembic upgrade head` works.
    """

    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "devices" not in tables:
        op.create_table(
            "devices",
            sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("hardware_id", sa.String(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("last_seen_at", sa.DateTime(), nullable=True),
            sa.Column("is_online", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("uptime", sa.Float(), nullable=True),
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
            sa.UniqueConstraint("hardware_id", name="uq_devices_hardware_id"),
        )

    else:
        device_columns = {c["name"] for c in inspector.get_columns("devices")}
        existing_uniques = {uc["name"] for uc in inspector.get_unique_constraints("devices")}

        with op.batch_alter_table("devices", schema=None) as batch_op:
            if "hardware_id" not in device_columns:
                batch_op.add_column(sa.Column("hardware_id", sa.String(), nullable=True))
            if "uq_devices_hardware_id" not in existing_uniques:
                batch_op.create_unique_constraint("uq_devices_hardware_id", ["hardware_id"])
            # Backward-compat: some earlier experimental schema had this column.
            if "battery_level" in device_columns:
                batch_op.drop_column("battery_level")

    # Create related tables if missing.
    tables = set(inspector.get_table_names())

    if "device_logs" not in tables:
        op.create_table(
            "device_logs",
            sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
            sa.Column("device_id", sa.Uuid(), sa.ForeignKey("devices.id"), nullable=False),
            sa.Column("level", sa.String(), nullable=False),
            sa.Column("message", sa.String(), nullable=False),
            sa.Column(
                "recorded_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
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
        )
        op.create_index("idx_device_logs_device_id", "device_logs", ["device_id"])
        op.create_index("idx_device_logs_level", "device_logs", ["level"])
        op.create_index("idx_device_logs_recorded_at", "device_logs", ["recorded_at"])

    if "device_images" not in tables:
        op.create_table(
            "device_images",
            sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
            sa.Column("device_id", sa.Uuid(), sa.ForeignKey("devices.id"), nullable=False),
            sa.Column("plant_id", sa.Uuid(), sa.ForeignKey("plants.id"), nullable=True),
            sa.Column("zone_id", sa.Uuid(), sa.ForeignKey("zones.id"), nullable=True),
            sa.Column("image_url", sa.String(), nullable=False),
            sa.Column("type", sa.String(), nullable=False),
            sa.Column("captured_at", sa.DateTime(), nullable=False),
            sa.Column("metadata_json", sa.String(), nullable=True),
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
        )
        op.create_index("idx_device_images_device_id", "device_images", ["device_id"])
        op.create_index("idx_device_images_plant_id", "device_images", ["plant_id"])
        op.create_index("idx_device_images_zone_id", "device_images", ["zone_id"])
        op.create_index("idx_device_images_captured_at", "device_images", ["captured_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    # Drop dependent tables first.
    if "device_images" in tables:
        op.drop_index("idx_device_images_captured_at", table_name="device_images")
        op.drop_index("idx_device_images_zone_id", table_name="device_images")
        op.drop_index("idx_device_images_plant_id", table_name="device_images")
        op.drop_index("idx_device_images_device_id", table_name="device_images")
        op.drop_table("device_images")

    if "device_logs" in tables:
        op.drop_index("idx_device_logs_recorded_at", table_name="device_logs")
        op.drop_index("idx_device_logs_level", table_name="device_logs")
        op.drop_index("idx_device_logs_device_id", table_name="device_logs")
        op.drop_table("device_logs")

    # Revert devices changes if the table exists.
    if "devices" in tables:
        device_columns = {c["name"] for c in inspector.get_columns("devices")}
        existing_uniques = {uc["name"] for uc in inspector.get_unique_constraints("devices")}

        with op.batch_alter_table("devices", schema=None) as batch_op:
            if "uq_devices_hardware_id" in existing_uniques:
                batch_op.drop_constraint("uq_devices_hardware_id", type_="unique")
            if "hardware_id" in device_columns:
                batch_op.drop_column("hardware_id")
            # Restore legacy column if you previously relied on it.
            if "battery_level" not in device_columns:
                batch_op.add_column(sa.Column("battery_level", sa.FLOAT(), nullable=True))
