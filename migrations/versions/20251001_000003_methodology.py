"""Add allowable variation column to methodologies

Revision ID: 20251001_000003_methodology
Revises: 20251001_000002_data_model
Create Date: 2025-10-01 07:45:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251001_000003_methodology"
down_revision = "20251001_000002_data_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "methodologies",
        sa.Column("allowable_variation_pct", sa.Float(), nullable=True),
    )
    op.alter_column(
        "methodology_points",
        "point_type",
        type_=sa.String(length=32),
        existing_type=postgresql.ENUM("bool", "clause", "custom", name="methodology_point_type"),
        postgresql_using="point_type::text",
        server_default=sa.text("'bool'"),
    )
    op.execute("DROP TYPE IF EXISTS methodology_point_type")


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS methodology_point_type")
    enum_type = postgresql.ENUM("bool", "clause", "custom", name="methodology_point_type")
    enum_type.create(op.get_bind(), checkfirst=False)
    op.alter_column(
        "methodology_points",
        "point_type",
        type_=enum_type,
        existing_type=sa.String(length=32),
        postgresql_using="point_type::methodology_point_type",
        server_default=sa.text("'bool'"),
    )
    op.drop_column("methodologies", "allowable_variation_pct")
