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
