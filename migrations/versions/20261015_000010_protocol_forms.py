"""Protocol forms as entities, and the modification axis

Revision ID: 20261015_000010_protocol_forms
Revises: 20261014_000009_template_binding_rules
Create Date: 2026-10-15 06:30:00.000000

The catalogue needs two things the flat rule list cannot give:

* **forms as entities with a parent** — so the interface can show a base form and what derives from
  it. ``protocol_forms`` is seeded from the current ``TEMPLATES`` (``code`` == ``template_id``),
  with the level-meter sub-forms pointing at ``level_meter`` as their parent. Everything is
  ``renderer = 'html'`` for now: those forms are still rendered by a file in ``app/templates`` and
  are not editable until the form editor lands;
* **the modification axis** — Arshin does not normalise modifications (``FMP51``,
  ``Levelflex FMP51``, ``мод. FMP51``, ``901.1/3100``), and inside one type the execution decides
  the table shape. The level-meter sub-forms therefore get rules by modification, while the
  registration-number rules stay as a fallback.

The seeded modification rules are a starting point, not the truth: they exist so the interface has
something real to show, and they are meant to be corrected there.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "20261015_000010_protocol_forms"
down_revision = "20261014_000009_template_binding_rules"
branch_labels = None
depends_on = None


# (code, title, instrument_kind, parent_code, renderer)
_SEED_FORMS: list[tuple[str, str, str, str | None, str]] = [
    ("pressure_common", "Манометры / датчики давления — общий", "manometers", None, "html"),
    (
        "pressure_sensor",
        "Датчики давления с токовым выходом 4–20 мА",
        "manometers",
        None,
        "html",
    ),
    ("controller_43790_12", "Контроллеры 43790-12", "controllers", None, "html"),
    (
        "controller_65685_16",
        "Контроллеры программируемые логические СК-1000 (65685-16)",
        "controllers",
        None,
        "html",
    ),
    ("rtd_platinum", "Термопреобразователи сопротивления", "thermometers", None, "html"),
    ("level_meter", "Уровнемеры", "level_meters", None, "html"),
    (
        "level_meter_two_tables",
        "Уровнемеры — две таблицы (жидкость и раздел)",
        "level_meters",
        "level_meter",
        "html",
    ),
    (
        "level_meter_current_output",
        "Уровнемеры — таблица мм и токовый выход",
        "level_meters",
        "level_meter",
        "html",
    ),
]

# (instrument_kind, match_field, match_value, template_id, priority)
_SEED_MODIFICATION_RULES: list[tuple[str, str, str, str, int]] = [
    ("level_meters", "modification", "901", "level_meter_two_tables", 26),
    ("level_meters", "modification", "902", "level_meter_two_tables", 26),
    ("level_meters", "modification", "FMP51", "level_meter_current_output", 26),
]


def upgrade() -> None:
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
        sa.Column("notes", sa.String(length=1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_protocol_forms_code"),
    )
    op.create_index("ix_protocol_forms_instrument_kind", "protocol_forms", ["instrument_kind"])

    forms_table = sa.table(
        "protocol_forms",
        sa.column("code", sa.String),
        sa.column("title", sa.String),
        sa.column("instrument_kind", sa.String),
        sa.column("parent_code", sa.String),
        sa.column("renderer", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        forms_table,
        [
            {
                "code": code,
                "title": title,
                "instrument_kind": kind,
                "parent_code": parent,
                "renderer": renderer,
                "is_active": True,
            }
            for code, title, kind, parent, renderer in _SEED_FORMS
        ],
    )

    rules_table = sa.table(
        "template_binding_rules",
        sa.column("instrument_kind", sa.String),
        sa.column("match_field", sa.String),
        sa.column("match_value", sa.String),
        sa.column("template_id", sa.String),
        sa.column("priority", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        rules_table,
        [
            {
                "instrument_kind": kind,
                "match_field": match_field,
                "match_value": match_value,
                "template_id": template_id,
                "priority": priority,
                "is_active": True,
            }
            for kind, match_field, match_value, template_id, priority in _SEED_MODIFICATION_RULES
        ],
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM template_binding_rules WHERE match_field = 'modification'"))
    op.drop_index("ix_protocol_forms_instrument_kind", table_name="protocol_forms")
    op.drop_table("protocol_forms")
