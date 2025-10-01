"""Add instrument_kind to verification registry entries

Revision ID: 20251010_000004_add_instrument_kind
Revises: 20251001_000003_methodology
Create Date: 2025-10-10 08:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251010_000004_add_instrument_kind"
down_revision = "20251001_000003_methodology"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(64)")
    op.add_column(
        "verification_registry_entries",
        sa.Column("instrument_kind", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_verification_registry_entries_instrument_kind"),
        "verification_registry_entries",
        ["instrument_kind"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_verification_registry_entries_instrument_kind"),
        table_name="verification_registry_entries",
    )
    op.drop_column("verification_registry_entries", "instrument_kind")
