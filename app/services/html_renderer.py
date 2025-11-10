from __future__ import annotations
# isort: skip_file

import re
from pathlib import Path
from typing import Any

from jinja2 import StrictUndefined
from starlette.templating import Jinja2Templates

from app.services.templates import resolve_template_id


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


def _template_name_from_context(ctx: dict[str, Any]) -> str:
    method_code = (ctx.get("methodology_full") or ctx.get("method_code") or "").strip()
    mitype_number = (ctx.get("mitypeNumber") or "").strip()
    mitype_title = (ctx.get("device_info") or "").strip()
    tpl_id = resolve_template_id(method_code, mitype_number, mitype_title)

    # simple mapping id -> file
    if tpl_id == "controller_43790_12":
        return "controller_43790_12.html"
    if tpl_id == "pressure_common":
        return "manometer.html"
    return "manometer.html"


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
    ctx.setdefault("etalon_entries", [])
    ctx.setdefault("etalon_lines", [])
    ctx.setdefault("etalon_certificates", [])

    if "allowable_variation" not in ctx or ctx["allowable_variation"] is None:
        pct = ctx.get("allowable_variation_pct")
        if isinstance(pct, int | float):
            ctx["allowable_variation"] = f"{pct:.2f}"
        elif isinstance(pct, str):
            ctx["allowable_variation"] = pct
        else:
            ctx["allowable_variation"] = ""

    ctx["temperature_plain"] = _normalize_temperature_plain(ctx.get("temperature_plain"))

    template = _templates.get_template(name)
    return template.render(ctx)
