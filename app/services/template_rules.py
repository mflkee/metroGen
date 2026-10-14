"""Resolution of the protocol form (template) for a verification row.

The mapping is data first: rules stored in ``template_binding_rules`` (matched by instrument kind
and a condition, in priority order), then the methodology's default form, and only then the
built-in heuristics in :mod:`app.services.templates`. The first two need the database, so they are
cached for a short while — a generation run resolves a form per row, and the rules change rarely.
The editing endpoints call :func:`invalidate` after every change, and the cache also expires on its
own so a second worker would converge.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.templates import resolve_template_id

logger = logging.getLogger(__name__)

MATCH_FIELDS = ("mitype_number", "title_keyword", "methodology_code")
INSTRUMENT_KINDS = ("manometers", "controllers", "thermometers", "level_meters")

_CACHE_TTL_SECONDS = 30.0


@dataclass(frozen=True)
class FormResolution:
    """The form a row resolves to, and why."""

    template_id: str
    source: str  # "override" | "rule" | "methodology" | "fallback"
    rule_id: int | None = None


@dataclass(frozen=True)
class _Rule:
    id: int
    instrument_kind: str
    match_field: str
    match_value: str
    template_id: str
    priority: int


_cache: tuple[list[_Rule], dict[str, str]] | None = None
_cache_at: float = 0.0


def invalidate() -> None:
    """Drop the cached rules so the next resolution reloads them."""
    global _cache, _cache_at
    _cache = None
    _cache_at = 0.0


async def _load(session: AsyncSession) -> tuple[list[_Rule], dict[str, str]]:
    from app.db.models import Methodology, TemplateBindingRule

    rule_rows = (
        (
            await session.execute(
                select(TemplateBindingRule)
                .where(TemplateBindingRule.is_active.is_(True))
                .order_by(TemplateBindingRule.priority.asc(), TemplateBindingRule.id.asc())
            )
        )
        .scalars()
        .all()
    )
    rules = [
        _Rule(
            id=row.id,
            instrument_kind=row.instrument_kind or "",
            match_field=row.match_field or "",
            match_value=row.match_value or "",
            template_id=row.template_id or "",
            priority=row.priority or 0,
        )
        for row in rule_rows
    ]

    methodology_rows = (
        await session.execute(
            select(Methodology.code, Methodology.template_id).where(
                Methodology.template_id.isnot(None)
            )
        )
    ).all()
    methodology_forms = {
        str(code).strip().upper(): str(template_id).strip()
        for code, template_id in methodology_rows
        if code and template_id
    }
    return rules, methodology_forms


async def _data(session: AsyncSession | None) -> tuple[list[_Rule], dict[str, str]]:
    global _cache, _cache_at
    if _cache is not None and (time.monotonic() - _cache_at) < _CACHE_TTL_SECONDS:
        return _cache
    if session is None:
        return _cache or ([], {})

    try:
        _cache = await _load(session)
        _cache_at = time.monotonic()
    except Exception as exc:  # pragma: no cover - defensive, the caller falls back to heuristics
        logger.warning("template rules: load failed (%s); falling back to heuristics", exc)
        if _cache is None:
            _cache = ([], {})
    return _cache


def _matches(rule: _Rule, *, method_code: str, mitype_number: str, mitype_title: str) -> bool:
    value = (rule.match_value or "").strip().upper()
    if not value:
        return False

    if rule.match_field == "mitype_number":
        return (mitype_number or "").strip().upper() == value

    if rule.match_field == "title_keyword":
        title = (mitype_title or "").upper()
        keywords = [keyword.strip() for keyword in value.split(",") if keyword.strip()]
        return bool(keywords) and all(keyword in title for keyword in keywords)

    if rule.match_field == "methodology_code":
        return value in (method_code or "").upper()

    return False


async def resolve_form(
    session: AsyncSession | None = None,
    *,
    method_code: str | None = None,
    mitype_number: str | None = None,
    mitype_title: str | None = None,
    instrument_kind: str | None = None,
    override: str | None = None,
) -> FormResolution:
    """Resolve the protocol form: override → rules → methodology default → heuristics."""

    if override and override.strip():
        return FormResolution(template_id=override.strip(), source="override")

    rules, methodology_forms = await _data(session)
    kind = (instrument_kind or "").strip().lower()
    for rule in rules:
        if kind and rule.instrument_kind.strip().lower() != kind:
            continue
        if _matches(
            rule,
            method_code=method_code or "",
            mitype_number=mitype_number or "",
            mitype_title=mitype_title or "",
        ):
            return FormResolution(template_id=rule.template_id, source="rule", rule_id=rule.id)

    code = (method_code or "").strip().upper()
    if code:
        for methodology_code, template_id in methodology_forms.items():
            if methodology_code and methodology_code in code:
                return FormResolution(template_id=template_id, source="methodology")

    fallback = resolve_template_id(method_code or "", mitype_number or "", mitype_title or "")
    return FormResolution(template_id=fallback or "pressure_common", source="fallback")
