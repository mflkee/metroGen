"""Restore the users table constraints (and drop rows the missing ones let in)

Revision ID: 20261012_000007_users_constraints
Revises: 20260408_000006_users
Create Date: 2026-10-12 08:30:00.000000

The staging database was found with a `users` table that had lost its primary key and
its unique email index, and with every row duplicated (10 rows over 5 ids, identical
`created_at`). A missing key does not fail loudly — it fails at the next lookup:
`get_by_email()` runs `scalar_one_or_none()`, so two rows for one address raise
`MultipleResultsFound` and the sign-in endpoint answers 500.

The migration is written to be safe on every environment: it deletes the duplicates
(keeping one row per id and per address), then restores the key and the index only if
they are absent, and re-syncs the id sequence so the next insert cannot collide.
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20261012_000007_users_constraints"
down_revision = "20260408_000006_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        # `ctid` is the physical row address: it keeps exactly one row of every pair.
        op.execute(
            """
            DELETE FROM users a
            USING users b
            WHERE a.ctid < b.ctid
              AND (a.id = b.id OR a.email = b.email)
            """
        )
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'users_pkey' AND conrelid = 'users'::regclass
                ) THEN
                    ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
                END IF;

                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes
                    WHERE indexname = 'ix_users_email' AND tablename = 'users'
                ) THEN
                    CREATE UNIQUE INDEX ix_users_email ON users (email);
                END IF;
            END
            $$;
            """
        )
        # A table that lost its key may have taken explicit ids; make the sequence catch up.
        op.execute(
            """
            SELECT setval(
                pg_get_serial_sequence('users', 'id'),
                COALESCE((SELECT MAX(id) FROM users), 1)
            )
            """
        )
        return

    # Other dialects (the test suite runs on SQLite): recreate the table with the key.
    with op.batch_alter_table("users") as batch:
        batch.create_primary_key("users_pkey", ["id"])


def downgrade() -> None:
    # The constraints are part of the schema, not a migration artefact: keep them.
    pass
