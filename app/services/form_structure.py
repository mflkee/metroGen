"""The structure of a protocol form: validation, inheritance, comparison and a preview.

A form's shape is data (see the change ``protocol-form-editor``): sections → tables → columns →
rows (measurement points). Values stay in the generators; the structure decides what the table
*is*.

Inheritance is an overlay, not a copy: a derived form stores only what it changes, keyed by the
path in the structure (items are matched by their ``id``). That makes "edit the base, derived forms
follow" the natural behaviour, and "what does this form override" a plain list of overlay keys.
"""

from __future__ import annotations

from html import escape
from typing import Any

STRUCTURE_SCHEMA = 1

#: Item lists whose entries are identified by `id` (merged/removed by id).
_LIST_KEYS = ("sections", "blocks", "columns", "rows")


def validate_structure(structure: Any) -> list[str]:
    """Return the problems of a structure; an empty list means it is usable."""
    problems: list[str] = []
    if not isinstance(structure, dict):
        return ["structure must be an object"]

    schema = structure.get("schema", STRUCTURE_SCHEMA)
    if not isinstance(schema, int) or schema < 1:
        problems.append("schema must be a positive integer")
    elif schema > STRUCTURE_SCHEMA:
        problems.append(f"schema {schema} is newer than this build supports ({STRUCTURE_SCHEMA})")

    sections = structure.get("sections")
    if not isinstance(sections, list):
        problems.append("sections must be a list")
        return problems

    seen_sections: set[str] = set()
    for section_index, section in enumerate(sections):
        if not isinstance(section, dict):
            problems.append(f"sections[{section_index}] must be an object")
            continue
        section_id = section.get("id")
        if not isinstance(section_id, str) or not section_id:
            problems.append(f"sections[{section_index}] needs a non-empty id")
        elif section_id in seen_sections:
            problems.append(f"duplicate section id '{section_id}'")
        else:
            seen_sections.add(section_id)

        blocks = section.get("blocks", [])
        if not isinstance(blocks, list):
            problems.append(f"section '{section_id}' blocks must be a list")
            continue
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                problems.append(f"section '{section_id}' blocks[{block_index}] must be an object")
                continue
            block_id = block.get("id")
            if not isinstance(block_id, str) or not block_id:
                problems.append(f"section '{section_id}' blocks[{block_index}] needs an id")
            block_type = block.get("type")
            if block_type not in ("text", "table"):
                problems.append(f"block '{block_id}' type must be 'text' or 'table'")
                continue
            if block_type == "text":
                continue

            columns = block.get("columns", [])
            if not isinstance(columns, list) or not columns:
                problems.append(f"table '{block_id}' needs at least one column")
                continue
            for column_index, column in enumerate(columns):
                if not isinstance(column, dict) or not column.get("id"):
                    problems.append(f"table '{block_id}' columns[{column_index}] needs an id")

            rows = block.get("rows", [])
            if not isinstance(rows, list):
                problems.append(f"table '{block_id}' rows must be a list")
                continue
            for row_index, row in enumerate(rows):
                if not isinstance(row, dict) or not row.get("id"):
                    problems.append(f"table '{block_id}' rows[{row_index}] needs an id")

    return problems


def _merge_node(base: Any, patch: Any) -> Any:
    if patch is None:
        return base
    if not isinstance(patch, dict) or not isinstance(base, dict):
        return patch

    result: dict[str, Any] = dict(base)
    for key, value in patch.items():
        if key == "_deleted":
            continue
        if isinstance(value, list) and isinstance(result.get(key), list):
            result[key] = _merge_list(result[key], value)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_node(result[key], value)
        else:
            result[key] = value
    return result


def _merge_list(base_items: list[Any], patch_items: list[Any]) -> list[Any]:
    result: list[Any] = [dict(item) if isinstance(item, dict) else item for item in base_items]
    index: dict[str, int] = {
        item["id"]: position
        for position, item in enumerate(result)
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    for item in patch_items:
        if not isinstance(item, dict):
            result.append(item)
            continue

        item_id = item.get("id")
        if item.get("_deleted"):
            if isinstance(item_id, str) and item_id in index:
                result[index[item_id]] = None
            continue

        if isinstance(item_id, str) and item_id in index:
            position = index[item_id]
            result[position] = _merge_node(result[position], item)
        else:
            result.append(item)
            if isinstance(item_id, str):
                index[item_id] = len(result) - 1

    return [item for item in result if item is not None]


def resolve_structure(code: str, forms: dict[str, Any], *, max_depth: int = 16) -> dict[str, Any]:
    """Resolve a form's structure by walking the parent chain and applying each overlay."""
    chain: list[Any] = []
    current = forms.get(code)
    depth = 0
    while current is not None and depth <= max_depth:
        chain.append(current)
        parent_code = getattr(current, "parent_code", None)
        current = forms.get(parent_code) if parent_code else None
        depth += 1

    structure: dict[str, Any] = {}
    for form in reversed(chain):  # root first, then each derived form's own parts
        own = getattr(form, "structure", None)
        if isinstance(own, dict):
            structure = _merge_node(structure, own)
        overlay = getattr(form, "overlay", None)
        if isinstance(overlay, dict):
            structure = _merge_node(structure, overlay)
    return structure


def _flatten(node: Any, prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("id", "_deleted"):
                continue
            path = f"{prefix}/{key}" if prefix else key
            if isinstance(value, (dict, list)):
                flat.update(_flatten(value, path))
            else:
                flat[path] = value
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                flat.update(_flatten(item, f"{prefix}/{item['id']}"))
            else:
                flat.update(_flatten(item, prefix))
    return flat


def diff_structures(
    left: dict[str, Any] | None, right: dict[str, Any] | None
) -> list[dict[str, Any]]:
    """List the differences between two resolved structures, by path."""
    left_flat = _flatten(left or {})
    right_flat = _flatten(right or {})
    differences: list[dict[str, Any]] = []

    for path in sorted(set(left_flat) | set(right_flat)):
        before = left_flat.get(path)
        after = right_flat.get(path)
        if path not in left_flat:
            differences.append({"path": path, "kind": "added", "after": after})
        elif path not in right_flat:
            differences.append({"path": path, "kind": "removed", "before": before})
        elif before != after:
            differences.append({"path": path, "kind": "changed", "before": before, "after": after})

    return differences


def overlay_keys(overlay: dict[str, Any] | None) -> list[str]:
    """The paths a derived form overrides (its overlay, flattened)."""
    return sorted(_flatten(overlay or {}).keys())


def render_structure_preview(structure: dict[str, Any]) -> str:
    """Render the *shape* of a form as HTML, for the editor's preview.

    Values are not filled in here: the generators still produce them, and the form only takes over
    the protocol once its renderer moves to data (see the change tasks). The preview therefore
    shows which tables, columns and measurement points the form describes.
    """
    parts: list[str] = [
        "<!doctype html><html lang='ru'><head><meta charset='utf-8'>",
        "<title>Предпросмотр формы</title></head><body>",
        "<p class='preview-note'>Черновик формы: показана структура таблиц. "
        "Значения подставляются при генерации.</p>",
    ]

    for section in structure.get("sections") or []:
        if not isinstance(section, dict):
            continue
        parts.append(f"<h2>{escape(str(section.get('title') or section.get('id') or ''))}</h2>")
        for block in section.get("blocks") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                parts.append(f"<p>{escape(str(block.get('text') or ''))}</p>")
                continue
            if block.get("type") != "table":
                continue

            columns = [
                column for column in (block.get("columns") or []) if isinstance(column, dict)
            ]
            rows = [row for row in (block.get("rows") or []) if isinstance(row, dict)]
            parts.append("<table class='data-table'><thead><tr>")
            for column in columns:
                parts.append(
                    f"<th>{escape(str(column.get('title') or column.get('id') or ''))}</th>"
                )
            parts.append("</tr></thead><tbody>")
            for row in rows:
                parts.append("<tr>")
                for column_index, _column in enumerate(columns):
                    label = row.get("label") if column_index == 0 else ""
                    parts.append(f"<td>{escape(str(label or ''))}</td>")
                parts.append("</tr>")
            parts.append("</tbody></table>")
            parts.append(
                f"<p class='preview-meta'>Точек замера: {len(rows)}, колонок: {len(columns)}</p>"
            )

    parts.append("</body></html>")
    return "".join(parts)
