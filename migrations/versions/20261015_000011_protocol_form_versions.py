"""A form's structure, its overlay and its published versions

Revision ID: 20261015_000011_protocol_form_versions
Revises: 20261015_000010_protocol_forms
Create Date: 2026-10-15 09:10:00.000000

The form editor needs three things the catalogue did not have:

* ``protocol_forms.structure`` — the editable shape of a form (sections, tables, columns,
  measurement points). The column already exists from the catalogue migration;
* ``protocol_forms.overlay`` — what a derived form overrides. Inheritance is an overlay, not a
  copy: editing the base propagates to every derived form that did not override that part;
* ``protocol_form_versions`` — immutable snapshots of a published form. A draft lives in the form
  row; publishing fixes a snapshot, so generation (once a form moves to ``renderer = 'data'``)
  always uses something recoverable.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "20261015_000011_protocol_form_versions"
down_revision = "20261015_000010_protocol_forms"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("protocol_forms", sa.Column("overlay", JSONB, nullable=True))

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


def downgrade() -> None:
    op.drop_index("ix_protocol_form_versions_form_id", table_name="protocol_form_versions")
    op.drop_table("protocol_form_versions")
    op.drop_column("protocol_forms", "overlay")
