"""The form structure: validation, inheritance (overlay merge), comparison and preview."""

from dataclasses import dataclass, field
from typing import Any

from app.services import form_structure


def _structure(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema": 1,
        "sections": [
            {
                "id": "main",
                "title": "Результаты поверки",
                "blocks": [
                    {
                        "id": "points",
                        "type": "table",
                        "columns": [
                            {"id": "ref", "title": "Эталон"},
                            {"id": "si", "title": "Показания СИ"},
                        ],
                        "rows": [
                            {"id": "p0", "kind": "point", "at": 0},
                            {"id": "p1", "kind": "point", "at": 0.5},
                        ],
                    }
                ],
            }
        ],
    }
    base.update(overrides)
    return base


@dataclass
class _Form:
    code: str
    parent_code: str | None = None
    structure: dict[str, Any] | None = None
    overlay: dict[str, Any] | None = field(default=None)


def test_valid_structure_has_no_problems():
    assert form_structure.validate_structure(_structure()) == []


def test_invalid_structures_are_reported():
    assert form_structure.validate_structure("nope") == ["structure must be an object"]
    assert form_structure.validate_structure({"schema": 99, "sections": []})

    duplicate = _structure(
        sections=[
            {"id": "main", "blocks": []},
            {"id": "main", "blocks": []},
        ]
    )
    assert any(
        "duplicate section id" in problem
        for problem in form_structure.validate_structure(duplicate)
    )

    no_columns = _structure(
        sections=[{"id": "main", "blocks": [{"id": "points", "type": "table", "columns": []}]}]
    )
    assert any(
        "at least one column" in problem
        for problem in form_structure.validate_structure(no_columns)
    )

    bad_type = _structure(sections=[{"id": "main", "blocks": [{"id": "x", "type": "chart"}]}])
    assert any(
        "must be 'text' or 'table'" in problem
        for problem in form_structure.validate_structure(bad_type)
    )


def test_overlay_adds_a_point_and_changes_a_column_title():
    base = _structure()
    overlay = {
        "sections": [
            {
                "id": "main",
                "blocks": [
                    {
                        "id": "points",
                        "columns": [{"id": "si", "title": "Показания прибора"}],
                        "rows": [{"id": "p2", "kind": "point", "at": 1.0}],
                    }
                ],
            }
        ]
    }

    merged = form_structure.resolve_structure(
        "derived",
        {
            "base": _Form(code="base", structure=base),
            "derived": _Form(code="derived", parent_code="base", overlay=overlay),
        },
    )

    table = merged["sections"][0]["blocks"][0]
    assert [row["id"] for row in table["rows"]] == ["p0", "p1", "p2"]
    assert [column["title"] for column in table["columns"]] == ["Эталон", "Показания прибора"]


def test_overlay_can_remove_a_row():
    overlay = {
        "sections": [
            {"id": "main", "blocks": [{"id": "points", "rows": [{"id": "p0", "_deleted": True}]}]}
        ]
    }

    merged = form_structure.resolve_structure(
        "derived",
        {
            "base": _Form(code="base", structure=_structure()),
            "derived": _Form(code="derived", parent_code="base", overlay=overlay),
        },
    )

    assert [row["id"] for row in merged["sections"][0]["blocks"][0]["rows"]] == ["p1"]


def test_base_change_reaches_a_derived_form_without_an_override():
    derived = _Form(code="derived", parent_code="base", overlay={})

    before = form_structure.resolve_structure(
        "derived", {"base": _Form(code="base", structure=_structure()), "derived": derived}
    )
    after = form_structure.resolve_structure(
        "derived",
        {
            "base": _Form(
                code="base",
                structure=_structure(
                    sections=[
                        {
                            "id": "main",
                            "blocks": [
                                {
                                    "id": "points",
                                    "columns": [
                                        {"id": "ref", "title": "Эталон"},
                                        {"id": "si", "title": "Показания СИ"},
                                        {"id": "err", "title": "Погрешность"},
                                    ],
                                    "rows": [{"id": "p0", "kind": "point", "at": 0}],
                                }
                            ],
                        }
                    ]
                ),
            ),
            "derived": derived,
        },
    )

    assert len(before["sections"][0]["blocks"][0]["columns"]) == 2
    assert len(after["sections"][0]["blocks"][0]["columns"]) == 3


def test_overlay_keys_lists_what_a_form_overrides():
    overlay = {"sections": [{"id": "main", "blocks": [{"id": "points", "rows": [{"id": "p2"}]}]}]}
    keys = form_structure.overlay_keys(overlay)
    assert "sections/main/blocks/points/rows/p2" in keys


def test_diff_reports_added_changed_and_removed():
    left = _structure()
    right = _structure(
        sections=[
            {
                "id": "main",
                "title": "Результаты поверки (черновик)",
                "blocks": [
                    {
                        "id": "points",
                        "type": "table",
                        "columns": [
                            {"id": "ref", "title": "Эталон"},
                            {"id": "si", "title": "Показания СИ"},
                            {"id": "err", "title": "Погрешность"},
                        ],
                        "rows": [{"id": "p0", "kind": "point", "at": 0}],
                    }
                ],
            }
        ]
    )

    differences = {
        item["path"]: item["kind"] for item in form_structure.diff_structures(left, right)
    }

    assert differences["sections/main/title"] == "changed"
    assert differences["sections/main/blocks/points/columns/err/title"] == "added"
    assert differences["sections/main/blocks/points/rows/p1/at"] == "removed"


def test_preview_renders_the_shape_of_the_form():
    html = form_structure.render_structure_preview(_structure())

    assert "Результаты поверки" in html
    assert "Показания СИ" in html
    assert "Точек замера: 2, колонок: 2" in html
    assert "data-table" in html


def test_form_structures_extract_points_and_columns():
    from app.services import form_structures

    structure = _structure()
    assert form_structures.point_fractions(structure) == [0.0, 0.5]
    assert [column["id"] for column in form_structures.table_columns(structure) or []] == [
        "ref",
        "si",
    ]

    assert form_structures.point_fractions(None) is None
    assert form_structures.point_fractions({"sections": [{"id": "s", "blocks": []}]}) is None


def test_build_structure_table_resolves_values_by_source():
    from app.services import form_structures

    structure = {
        "schema": 1,
        "sections": [
            {
                "id": "main",
                "blocks": [
                    {
                        "id": "points",
                        "type": "table",
                        "columns": [
                            {"id": "si", "title": "Показания", "source": "si_fwd"},
                            {"id": "tol", "title": "Допуск", "source": "allowable_error"},
                            {"id": "mystery", "title": "Без источника", "source": "nope"},
                        ],
                        "rows": [{"id": "p0", "at": 0}, {"id": "p1", "at": 1}],
                    }
                ],
            }
        ],
    }
    rows = [
        {"si_fwd": "1.00", "si_rev": "1.01"},
        {"si_fwd": "2.00", "si_rev": "2.01"},
    ]
    context = {"allowable_error": "1.50"}

    table = form_structures.build_structure_table(structure, rows, context)

    assert table is not None
    assert [column["title"] for column in table["columns"]] == [
        "Показания",
        "Допуск",
        "Без источника",
    ]
    assert table["rows"] == [["1.00", "1.50", ""], ["2.00", "1.50", ""]]


def test_build_structure_table_needs_rows_and_columns():
    from app.services import form_structures

    structure = _structure()
    assert form_structures.build_structure_table(structure, [], {}) is None
    assert form_structures.build_structure_table(structure, [{"si_val": "1"}], {}) is not None
    assert form_structures.build_structure_table(None, [{"a": "1"}], {}) is None


def test_validate_structure_rejects_an_empty_column_source():
    broken = _structure(
        sections=[
            {
                "id": "main",
                "blocks": [
                    {
                        "id": "points",
                        "type": "table",
                        "columns": [{"id": "ref", "title": "Эталон", "source": "  "}],
                        "rows": [{"id": "p0", "at": 0}],
                    }
                ],
            }
        ]
    )
    problems = form_structure.validate_structure(broken)
    assert any("source must be a non-empty string" in problem for problem in problems)


def test_generator_takes_the_points_from_the_form_structure():
    from app.services.generators.base import FixedPctTol, GenInput, steps_from_fractions
    from app.services.generators.pressure_common import GENERATOR

    assert steps_from_fractions(4.0, [0, 0.5, 1.0]) == [0.0, 2.0, 4.0]
    assert steps_from_fractions(4.0, None) is None
    assert steps_from_fractions(4.0, []) is None

    def make(fractions):
        return GenInput(
            range_min=0.0,
            range_max=4.0,
            unit="кгс/см²",
            points=8,
            allowable_error=FixedPctTol(1.5),
            allowable_variation=FixedPctTol(1.5),
            ctx={},
            point_fractions=fractions,
        )

    # Без структуры — прежнее поведение («красивые» шаги генератора, не меньше 8 точек).
    assert len(GENERATOR.generate(make(None))["rows"]) >= 8
    # Со структурой — ровно её точки замера.
    assert len(GENERATOR.generate(make([0, 0.5, 1.0]))["rows"]) == 3
    assert len(GENERATOR.generate(make([0, 0.25, 0.5, 0.75, 1.0]))["rows"]) == 5
