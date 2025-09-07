"""init schema

Revision ID: 000001
Revises: 
Create Date: 2025-09-06 00:00:01

"""
from __future__ import annotations
# isort: skip_file

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("supported_fields", sa.JSON(), nullable=True),
    )

    op.create_table(
        "owners",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("inn", sa.String(length=32), nullable=True),
    )
    op.create_index("ix_owners_inn", "owners", ["inn"], unique=False)

    op.create_table(
        "etalons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reg_number", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("certificate", sa.String(length=128), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
    )
    op.create_index("ix_etalons_reg_number", "etalons", ["reg_number"], unique=False)

    op.create_table(
        "protocols",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("number", sa.String(length=64), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("methodology", sa.String(length=255), nullable=True),
        sa.Column("vri_id", sa.String(length=64), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("owners.id")),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("templates.id")),
        sa.Column("etalon_id", sa.Integer(), sa.ForeignKey("etalons.id")),
        sa.Column("context", sa.JSON(), nullable=True),
    )
    op.create_index("ix_protocols_number", "protocols", ["number"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_protocols_number", table_name="protocols")
    op.drop_table("protocols")
    op.drop_index("ix_etalons_reg_number", table_name="etalons")
    op.drop_table("etalons")
    op.drop_index("ix_owners_inn", table_name="owners")
    op.drop_table("owners")
    op.drop_table("templates")
