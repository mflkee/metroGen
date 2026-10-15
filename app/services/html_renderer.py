from __future__ import annotations
# isort: skip_file

import logging
import re
from pathlib import Path
from typing import Any

from jinja2 import StrictUndefined
from starlette.templating import Jinja2Templates

from app.services.templates import TEMPLATES, resolve_template_id

logger = logging.getLogger(__name__)


_BASE_DIR = Path(__file__).resolve().parent.parent
_TPL_DIR = _BASE_DIR / "templates"


def _fmt2(value: Any) -> str:
    try:
        # format with 2 decimals, dot separator; template can replace if needed
        return f"{float(value):.2f}"
    except Exception:
        return str(value)


def _build_renderer() -> Jinja2Templates:
    templates = Jinja2Templates(directory=str(_TPL_DIR))
    # register filters
    templates.env.filters["fmt2"] = _fmt2
    templates.env.undefined = StrictUndefined
    return templates


_templates = _build_renderer()


_TEMP_VALUE_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def _normalize_temperature_plain(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    match = _TEMP_VALUE_RE.search(text)
    if not match:
        return text
    numeric = match.group(0).replace(",", ".")
    try:
        number = float(numeric)
    except ValueError:
        cleaned = match.group(0)
    else:
        cleaned = f"{number:.1f}".rstrip("0").rstrip(".")
    if not cleaned:
        cleaned = match.group(0)
    return cleaned.replace(".", ",")


def _normalize_humidity_plain(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    match = _TEMP_VALUE_RE.search(text)
    if not match:
        return text
    numeric = match.group(0).replace(",", ".")
    try:
        number = float(numeric)
    except ValueError:
        cleaned = match.group(0)
    else:
        # Excel percent-formatted cells usually come through openpyxl as 0.34 for 34%.
        if "%" not in text and 0 <= number <= 1:
            number *= 100
        cleaned = f"{number:.2f}".rstrip("0").rstrip(".")
    if not cleaned:
        cleaned = match.group(0)
    return cleaned.replace(".", ",")


def _display_or_fallback(value: Any, fallback: str = "") -> Any:
    if value is None:
        return fallback
    if isinstance(value, str) and not value.strip():
        return fallback
    return value


def _template_name_from_context(ctx: dict[str, Any]) -> str:
    """Pick the HTML file for the form the builder resolved.

    The resolved form arrives as ``context["template_id"]``; only when it is missing (an old
    caller, a hand-made context) is the form derived again from the context fields, and that
    fallback is logged so such callers can be fixed.
    """
    tpl_id = str(ctx.get("template_id") or "").strip()
    if not tpl_id:
        method_code = (ctx.get("methodology_full") or ctx.get("method_code") or "").strip()
        mitype_number = (ctx.get("mitypeNumber") or "").strip()
        mitype_title = (ctx.get("device_info") or "").strip()
        tpl_id = resolve_template_id(method_code, mitype_number, mitype_title)
        logger.warning(
            "protocol render: context has no template_id; derived %r from its fields", tpl_id
        )

    path = (TEMPLATES.get(tpl_id) or {}).get("path")
    if isinstance(path, str) and path:
        return path
    return "pressure.html"


def render_protocol_html(context: dict[str, Any]) -> str:
    """Render protocol HTML using Jinja2Templates.

    The template is chosen based on context via resolve_template_id.
    """
    name = _template_name_from_context(context)

    # Normalize commonly used fields for template compatibility
    ctx = dict(context)
    # expose aliases expected by template
    ctx.setdefault("unit_label", ctx.get("unit"))
    ctx.setdefault("allowable_error", ctx.get("allowable_error_fmt"))
    # plain numeric environment values (strings acceptable too)
    ctx.setdefault("temperature_plain", ctx.get("temperature"))
    ctx.setdefault("humidity_plain", ctx.get("humidity"))
    ctx.setdefault("allowable_note", "")
    ctx.setdefault("table_rows", [])
    ctx.setdefault("table_rows_b", [])
    ctx.setdefault("point_groups", [])
    ctx.setdefault("etalon_entries", [])
    ctx.setdefault("etalon_lines", [])
    ctx.setdefault("etalon_line", "")
    ctx.setdefault("etalon_line_top", "")
    ctx.setdefault("etalon_line_bottom", "")
    ctx.setdefault("etalon_certificates", [])
    ctx.setdefault("auxiliary_instruments", [])
    ctx.setdefault("auxiliary_instruments_requested", [])
    ctx.setdefault("measurement_range_text", "")
    ctx.setdefault("accuracy_class", "")
    ctx.setdefault("max_abs_error_value", "")
    ctx.setdefault("max_abs_error_unit", "")
    ctx.setdefault("max_variation_value", "")
    ctx.setdefault("max_variation_unit", "%")
    ctx.setdefault("show_abs_error_summary", False)
    ctx.setdefault("trainee_name", "")
    ctx.setdefault("trainee_sign_src", "")
    ctx.setdefault("trainee_sign_style", "display: none;")
    ctx.setdefault("trainee_note", "")
    ctx.setdefault("sign_src", "")
    ctx.setdefault("sign_style", "display: none;")
    ctx.setdefault("verification_failed", False)
    ctx.setdefault("hide_results_table", bool(ctx.get("verification_failed")))
    ctx.setdefault("conclusion_text", "")
    ctx.setdefault("header_name", "")
    ctx.setdefault("header_address", "")
    ctx.setdefault("header_accreditation", "")
    ctx.setdefault("methodology_point_items", [])
    ctx.setdefault("methodology_points", {})
    ctx.setdefault("methodology_code", "")
    ctx.setdefault("has_current_output_table", False)
    ctx.setdefault("insol_two_tables", False)
    ctx.setdefault("current_output_rows", [])
    # Таблица из структуры формы: ключа может не быть (рендер по шаблону) — при StrictUndefined
    # это должно быть явным None, иначе `{% if structure_table %}` падает.
    ctx.setdefault("structure_table", None)

    if "allowable_variation" not in ctx or ctx["allowable_variation"] is None:
        pct = ctx.get("allowable_variation_pct")
        if isinstance(pct, int | float):
            ctx["allowable_variation"] = f"{pct:.2f}"
        elif isinstance(pct, str):
            ctx["allowable_variation"] = pct
        else:
            ctx["allowable_variation"] = ""

    ctx["temperature_plain"] = _normalize_temperature_plain(
        _display_or_fallback(ctx.get("temperature_plain"))
    )
    ctx["humidity_plain"] = _normalize_humidity_plain(
        _display_or_fallback(ctx.get("humidity_plain"), fallback="///")
    )

    template = _templates.get_template(name)
    return template.render(ctx)
