"""Drop the protocol form entities

Revision ID: 20261015_000012_drop_protocol_forms
Revises: 20261015_000011_protocol_form_versions
Create Date: 2026-10-15 12:40:00.000000

The «Формы протоколов» section is removed: forms are no longer entities the service shows or edits.
The two tables it introduced (`protocol_forms` and `protocol_form_versions`) are read by nothing
after the removal — the only readers were the section's router and the structure service, both
deleted.

What stays is the *mapping*: `template_binding_rules` (the rules that select a form) and
`methodologies.template_id` (a methodology's default form) are what generation actually uses through
`resolve_form`, so they are untouched.

The downgrade recreates the schema (not the seeded rows): the tables only ever held metadata derived
from the template registry.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "20261015_000012_drop_protocol_forms"
down_revision = "20261015_000011_protocol_form_versions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_protocol_form_versions_form_id", table_name="protocol_form_versions")
    op.drop_table("protocol_form_versions")
    op.drop_index("ix_protocol_forms_instrument_kind", table_name="protocol_forms")
    op.drop_table("protocol_forms")


def downgrade() -> None:
    op.create_table(
        "protocol_forms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("instrument_kind", sa.String(length=64), nullable=False),
        sa.Column("parent_code", sa.String(length=64), nullable=True),
        sa.Column(
            "renderer", sa.String(length=16), nullable=False, server_default=sa.text("'html'")
        ),
        sa.Column("structure", JSONB, nullable=True),
        sa.Column("overlay", JSONB, nullable=True),
        sa.Column("notes", sa.String(length=1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_protocol_forms_code"),
    )
    op.create_index("ix_protocol_forms_instrument_kind", "protocol_forms", ["instrument_kind"])

    op.create_table(
        "protocol_form_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("form_id", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("structure_resolved", JSONB, nullable=True),
        sa.Column("overlay", JSONB, nullable=True),
        sa.Column("comment", sa.String(length=512), nullable=True),
        sa.Column("published_by", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["form_id"], ["protocol_forms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("form_id", "revision", name="uq_protocol_form_version"),
    )
    op.create_index("ix_protocol_form_versions_form_id", "protocol_form_versions", ["form_id"])
