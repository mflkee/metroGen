"""Add auxiliary verification instruments table

Revision ID: 20260302_000005_auxiliary_verification_instruments
Revises: 20251010_000004_add_instrument_kind
Create Date: 2026-03-02 12:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "20260302_000005_auxiliary_verification_instruments"
down_revision = "20251010_000004_add_instrument_kind"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(64)")
    op.create_table(
        "auxiliary_verification_instruments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reg_number", sa.String(length=128), nullable=False),
        sa.Column("normalized_serial", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("modification", sa.String(length=255), nullable=True),
        sa.Column("manufacture_num", sa.String(length=128), nullable=True),
        sa.Column("certificate_no", sa.String(length=128), nullable=True),
        sa.Column("verification_date", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reg_number", "normalized_serial", name="uq_aux_vi_reg_serial"),
    )
    op.create_index(
        op.f("ix_auxiliary_verification_instruments_reg_number"),
        "auxiliary_verification_instruments",
        ["reg_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auxiliary_verification_instruments_normalized_serial"),
        "auxiliary_verification_instruments",
        ["normalized_serial"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_auxiliary_verification_instruments_normalized_serial"),
        table_name="auxiliary_verification_instruments",
    )
    op.drop_index(
        op.f("ix_auxiliary_verification_instruments_reg_number"),
        table_name="auxiliary_verification_instruments",
    )
    op.drop_table("auxiliary_verification_instruments")
