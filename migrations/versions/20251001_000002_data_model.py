"""Expand data model with registry, instruments, etalons, methodologies

Revision ID: 20251001_000002_data_model
Revises: 20250906_000001_init
Create Date: 2025-10-01 06:20:00.000000
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op


# revision identifiers, used by Alembic.
revision = "20251001_000002_data_model"
down_revision = "20250906_000001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    methodology_point_type = postgresql.ENUM(
        "bool",
        "clause",
        "custom",
        name="methodology_point_type",
        create_type=False,
    )
    methodology_point_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "verification_registry_entries",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("source_file", String(512), nullable=False),
        Column("source_sheet", String(255), nullable=True),
        Column("loaded_at", DateTime, nullable=False, server_default=text("now()")),
        Column("row_index", Integer, nullable=False),
        Column("normalized_serial", String(128), nullable=True),
        Column("document_no", String(128), nullable=True),
        Column("protocol_no", String(128), nullable=True),
        Column("owner_name_raw", String(255), nullable=True),
        Column("methodology_raw", String(255), nullable=True),
        Column("verification_date", Date, nullable=True),
        Column("valid_to", Date, nullable=True),
        Column("payload", JSONB, nullable=True),
        Column("is_active", Boolean, nullable=False, server_default=text("true")),
        UniqueConstraint("source_file", "row_index", name="uq_registry_source_row"),
    )
    op.create_index(
        "ix_registry_serial",
        "verification_registry_entries",
        ["normalized_serial"],
    )
    op.create_index(
        "ix_registry_document",
        "verification_registry_entries",
        ["document_no"],
    )
    op.create_index(
        "ix_registry_protocol",
        "verification_registry_entries",
        ["protocol_no"],
    )

    op.create_table(
        "methodologies",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("code", String(128), nullable=False, unique=True),
        Column("title", String(255), nullable=False),
        Column("document", String(255), nullable=True),
        Column("notes", String(1024), nullable=True),
    )

    op.create_table(
        "methodology_aliases",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("methodology_id", Integer, ForeignKey("methodologies.id", ondelete="CASCADE"), nullable=False),
        Column("alias", String(255), nullable=False),
        Column("normalized_alias", String(255), nullable=False),
        Column("weight", Integer, nullable=False, server_default=text("100")),
        UniqueConstraint("normalized_alias", name="uq_methodology_alias_normalized"),
    )
    op.create_index(
        "ix_methodology_alias_methodology",
        "methodology_aliases",
        ["methodology_id"],
    )

    op.create_table(
        "methodology_points",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("methodology_id", Integer, ForeignKey("methodologies.id", ondelete="CASCADE"), nullable=False),
        Column("position", Integer, nullable=False),
        Column("label", String(512), nullable=False),
        Column("point_type", methodology_point_type, nullable=False, server_default="bool"),
        Column("default_text", String(1024), nullable=True),
        UniqueConstraint("methodology_id", "position", name="uq_methodology_points_order"),
    )
    op.create_index(
        "ix_methodology_points_methodology",
        "methodology_points",
        ["methodology_id"],
    )

    op.create_table(
        "owner_aliases",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("owner_id", Integer, ForeignKey("owners.id", ondelete="CASCADE"), nullable=False),
        Column("alias", String(255), nullable=False),
        Column("normalized_alias", String(255), nullable=False),
        UniqueConstraint("normalized_alias", name="uq_owner_alias_normalized"),
    )
    op.create_index(
        "ix_owner_alias_owner",
        "owner_aliases",
        ["owner_id"],
    )

    op.create_table(
        "etalon_devices",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("reg_number", String(128), nullable=False),
        Column("mitype_number", String(128), nullable=True),
        Column("title", String(255), nullable=True),
        Column("notation", String(255), nullable=True),
        Column("modification", String(255), nullable=True),
        Column("manufacture_num", String(128), nullable=True),
        Column("manufacture_year", Integer, nullable=True),
        Column("rank_code", String(64), nullable=True),
        Column("rank_title", String(255), nullable=True),
        Column("schema_title", String(255), nullable=True),
        Column("payload", JSONB, nullable=True),
        UniqueConstraint(
            "reg_number",
            "manufacture_num",
            name="uq_etalon_device_reg_manufacture",
        ),
    )
    op.create_index(
        "ix_etalon_devices_reg_number",
        "etalon_devices",
        ["reg_number"],
    )

    op.create_table(
        "etalon_certifications",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("etalon_device_id", Integer, ForeignKey("etalon_devices.id", ondelete="CASCADE"), nullable=False),
        Column("certificate_no", String(128), nullable=False),
        Column("verification_date", Date, nullable=True),
        Column("valid_to", Date, nullable=True),
        Column("source", String(64), nullable=False, server_default=text("'arshin'")),
        Column("payload", JSONB, nullable=True),
        UniqueConstraint(
            "etalon_device_id",
            "certificate_no",
            name="uq_etalon_certificates_unique",
        ),
    )
    op.create_index(
        "ix_etalon_cert_certificate",
        "etalon_certifications",
        ["certificate_no"],
    )
    op.create_index(
        "ix_etalon_cert_valid_to",
        "etalon_certifications",
        ["valid_to"],
    )

    op.create_table(
        "measuring_instruments",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("normalized_serial", String(128), nullable=False),
        Column("designation", String(255), nullable=True),
        Column("modification", String(255), nullable=True),
        Column("manufacture_year", Integer, nullable=True),
        Column("owner_id", Integer, ForeignKey("owners.id", ondelete="SET NULL"), nullable=True),
        Column("methodology_id", Integer, ForeignKey("methodologies.id", ondelete="SET NULL"), nullable=True),
        Column("registry_entry_id", Integer, ForeignKey("verification_registry_entries.id", ondelete="SET NULL"), nullable=True),
        Column("certificate_no", String(128), nullable=True),
        Column("certificate_valid_to", Date, nullable=True),
        Column("vri_id", String(64), nullable=True),
        Column("payload", JSONB, nullable=True),
        Column("created_at", DateTime, nullable=False, server_default=text("now()")),
        Column(
            "updated_at",
            DateTime,
            nullable=False,
            server_default=text("now()"),
            server_onupdate=text("now()"),
        ),
        UniqueConstraint("normalized_serial", "certificate_no", name="uq_instruments_serial_cert"),
    )
    op.create_index(
        "ix_instruments_serial",
        "measuring_instruments",
        ["normalized_serial"],
    )
    op.create_index(
        "ix_instruments_owner",
        "measuring_instruments",
        ["owner_id"],
    )
    op.create_index(
        "ix_instruments_methodology",
        "measuring_instruments",
        ["methodology_id"],
    )

    op.add_column(
        "protocols",
        Column("registry_entry_id", Integer, ForeignKey("verification_registry_entries.id", ondelete="SET NULL"), nullable=True),
    )
    op.add_column(
        "protocols",
        Column("measuring_instrument_id", Integer, ForeignKey("measuring_instruments.id", ondelete="SET NULL"), nullable=True),
    )
    op.add_column(
        "protocols",
        Column("etalon_certification_id", Integer, ForeignKey("etalon_certifications.id", ondelete="SET NULL"), nullable=True),
    )

    op.create_index(
        "ix_protocols_registry_entry",
        "protocols",
        ["registry_entry_id"],
    )
    op.create_index(
        "ix_protocols_measuring_instrument",
        "protocols",
        ["measuring_instrument_id"],
    )
    op.create_index(
        "ix_protocols_etalon_certification",
        "protocols",
        ["etalon_certification_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_protocols_etalon_certification", table_name="protocols")
    op.drop_index("ix_protocols_measuring_instrument", table_name="protocols")
    op.drop_index("ix_protocols_registry_entry", table_name="protocols")
    op.drop_column("protocols", "etalon_certification_id")
    op.drop_column("protocols", "measuring_instrument_id")
    op.drop_column("protocols", "registry_entry_id")

    op.drop_index("ix_instruments_methodology", table_name="measuring_instruments")
    op.drop_index("ix_instruments_owner", table_name="measuring_instruments")
    op.drop_index("ix_instruments_serial", table_name="measuring_instruments")
    op.drop_table("measuring_instruments")

    op.drop_index("ix_etalon_cert_valid_to", table_name="etalon_certifications")
    op.drop_index("ix_etalon_cert_certificate", table_name="etalon_certifications")
    op.drop_table("etalon_certifications")

    op.drop_index("ix_etalon_devices_reg_number", table_name="etalon_devices")
    op.drop_table("etalon_devices")

    op.drop_index("ix_owner_alias_owner", table_name="owner_aliases")
    op.drop_table("owner_aliases")

    op.drop_index("ix_methodology_points_methodology", table_name="methodology_points")
    op.drop_table("methodology_points")

    op.drop_index("ix_methodology_alias_methodology", table_name="methodology_aliases")
    op.drop_table("methodology_aliases")

    op.drop_table("methodologies")

    op.drop_index("ix_registry_protocol", table_name="verification_registry_entries")
    op.drop_index("ix_registry_document", table_name="verification_registry_entries")
    op.drop_index("ix_registry_serial", table_name="verification_registry_entries")
    op.drop_table("verification_registry_entries")

    op.execute("DROP TYPE IF EXISTS methodology_point_type")
