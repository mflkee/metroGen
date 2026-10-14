"""Form mapping rules and a methodology default form

Revision ID: 20261014_000009_template_binding_rules
Revises: 20261014_000008_role_synced_at
Create Date: 2026-10-14 09:40:00.000000

The protocol form used to be chosen by heuristics hardcoded in
``app/services/templates.resolve_template_id``. For level meters the sub-form (one table, two
tables, an extra current-output table) additionally lived inside the generator, keyed by the
registration number.

This migration makes the mapping data:

* ``template_binding_rules`` — instrument kind + condition → template, with a priority, so an
  administrator can see and control which form a given type resolves to;
* ``methodologies.template_id`` — a per-methodology default form.

The seed below mirrors the existing heuristics one-to-one (same relative order), so the rendered
forms do not change on rollout — the rules only make that behaviour visible and editable.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20261014_000009_template_binding_rules"
down_revision = "20261014_000008_role_synced_at"
branch_labels = None
depends_on = None


# (instrument_kind, match_field, match_value, template_id, priority)
_SEED_RULES: list[tuple[str, str, str, str, int]] = [
    # Термопреобразователи сопротивления
    ("thermometers", "methodology_code", "8.461", "rtd_platinum", 10),
    ("thermometers", "title_keyword", "8.461", "rtd_platinum", 10),
    ("thermometers", "title_keyword", "ТЕРМОПРЕОБРАЗОВ", "rtd_platinum", 10),
    # Контроллеры 43790-12
    ("controllers", "mitype_number", "43790-12", "controller_43790_12", 20),
    ("controllers", "title_keyword", "СГМ ЭРИС-100", "controller_43790_12", 20),
    # Контроллеры 65685-16 (СК-1000)
    ("controllers", "mitype_number", "65685-16", "controller_65685_16", 25),
    ("controllers", "title_keyword", "СК-1000", "controller_65685_16", 25),
    ("controllers", "methodology_code", "2539", "controller_65685_16", 25),
    # Датчики давления с токовым выходом
    ("manometers", "title_keyword", "ДАВЛЕН,ДАТЧИК", "pressure_sensor", 28),
    ("manometers", "title_keyword", "ДАВЛЕН,ПРЕОБРАЗОВАТЕЛ", "pressure_sensor", 28),
    ("manometers", "title_keyword", "ДАВЛЕН,ИЗМЕРИТЕЛ", "pressure_sensor", 28),
    # Манометры
    ("manometers", "mitype_number", "13535-93", "pressure_common", 30),
    ("manometers", "title_keyword", "МАНОМЕТР", "pressure_common", 30),
    # Уровнемеры: под-формы по номеру типа
    ("level_meters", "mitype_number", "86065-22", "level_meter_two_tables", 28),
    ("level_meters", "mitype_number", "47249-16", "level_meter_current_output", 28),
    # Уровнемеры: ключевые слова
    ("level_meters", "title_keyword", "УРОВНЕМЕР", "level_meter", 35),
    ("level_meters", "title_keyword", "УРОВН", "level_meter", 35),
    ("level_meters", "title_keyword", "LEVEL", "level_meter", 35),
    # Уровнемеры: номера типов из эвристики
    ("level_meters", "mitype_number", "53779-13", "level_meter", 36),
    ("level_meters", "mitype_number", "24715-03", "level_meter", 36),
    ("level_meters", "mitype_number", "17670-08", "level_meter", 36),
    ("level_meters", "mitype_number", "17670-13", "level_meter", 36),
    ("level_meters", "mitype_number", "26355-09", "level_meter", 36),
    ("level_meters", "mitype_number", "27284-04", "level_meter", 36),
    ("level_meters", "mitype_number", "27283-12", "level_meter", 36),
    ("level_meters", "mitype_number", "27284-09", "level_meter", 36),
    ("level_meters", "mitype_number", "36668-08", "level_meter", 36),
    ("level_meters", "mitype_number", "47249-11", "level_meter", 36),
    ("level_meters", "mitype_number", "47981-11", "level_meter", 36),
    ("level_meters", "mitype_number", "48164-11", "level_meter", 36),
    ("level_meters", "mitype_number", "53857-13", "level_meter", 36),
    ("level_meters", "mitype_number", "38679-08", "level_meter", 36),
]


def upgrade() -> None:
    op.add_column(
        "methodologies",
        sa.Column("template_id", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "template_binding_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instrument_kind", sa.String(length=64), nullable=False),
        sa.Column("match_field", sa.String(length=32), nullable=False),
        sa.Column("match_value", sa.String(length=255), nullable=False),
        sa.Column("template_id", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("100")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_template_binding_rules_instrument_kind",
        "template_binding_rules",
        ["instrument_kind"],
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
            for kind, match_field, match_value, template_id, priority in _SEED_RULES
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_template_binding_rules_instrument_kind", table_name="template_binding_rules")
    op.drop_table("template_binding_rules")
    op.drop_column("methodologies", "template_id")
