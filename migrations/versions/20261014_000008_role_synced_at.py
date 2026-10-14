"""Remember which registry role the local copy came from

Revision ID: 20261014_000008_role_synced_at
Revises: 20261012_000007_users_constraints
Create Date: 2026-10-14 06:30:00.000000

The role in metroGen is a mirror of the registry's; the row stores the value, but it did not
store *which* registry value it mirrors. Without that, a role change can only be pushed blindly:
the write says "make it ADMINISTRATOR" with no way to notice that the registry had moved on since
the screen was rendered, and the owner's newer change is lost without a word.

`role_synced_at` is that memory — the `role_updated_at` the copy was last built from, sent back to
the registry with the next write so a save based on a stale screen is refused (409) instead of
applied. Nothing is backfilled: NULL means "we do not know", and the first read takes the
registry's answer.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20261014_000008_role_synced_at"
down_revision = "20261012_000007_users_constraints"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role_synced_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "role_synced_at")
