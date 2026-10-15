"""The resolved structures of the forms that drive the protocol, cached for generation.

Generation reads the **published** structure: a draft may be half-edited, and a form only takes over
the protocol once its renderer is ``data``. The cache mirrors the rules cache (short TTL + explicit
invalidation after an edit), so a mass run does not query per row.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 30.0
_cache: dict[str, dict[str, Any]] | None = None
_cache_at: float = 0.0


def invalidate() -> None:
    """Drop the cached structures so the next generation reloads them."""
    global _cache, _cache_at
    _cache = None
    _cache_at = 0.0


async def _load(session: AsyncSession) -> dict[str, dict[str, Any]]:
    from app.db.models import ProtocolForm, ProtocolFormVersion

    forms = (
        (
            await session.execute(
                select(ProtocolForm).where(
                    ProtocolForm.renderer == "data",
                    ProtocolForm.is_active.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )
    if not forms:
        return {}

    result: dict[str, dict[str, Any]] = {}
    for form in forms:
        version = (
            await session.execute(
                select(ProtocolFormVersion)
                .where(ProtocolFormVersion.form_id == form.id)
                .order_by(ProtocolFormVersion.revision.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        structure = (version.structure_resolved if version is not None else None) or form.structure
        if isinstance(structure, dict) and structure:
            result[form.code] = structure
    return result


async def load(session: AsyncSession | None = None) -> dict[str, dict[str, Any]]:
    global _cache, _cache_at
    if _cache is not None and (time.monotonic() - _cache_at) < _CACHE_TTL_SECONDS:
        return _cache
    if session is None:
        return _cache or {}

    try:
        _cache = await _load(session)
        _cache_at = time.monotonic()
    except Exception as exc:  # pragma: no cover - defensive, generation falls back to defaults
        logger.warning("form structures: load failed (%s); using the generators' own points", exc)
        if _cache is None:
            _cache = {}
    return _cache


def _first_table(structure: dict[str, Any] | None) -> dict[str, Any] | None:
    for section in (structure or {}).get("sections") or []:
        for block in section.get("blocks") or []:
            if isinstance(block, dict) and block.get("type") == "table":
                return block
    return None


def point_fractions(structure: dict[str, Any] | None) -> list[float] | None:
    """The measurement points of the form's first table, as fractions of full scale."""
    table = _first_table(structure)
    if table is None:
        return None

    fractions: list[float] = []
    for row in table.get("rows") or []:
        if not isinstance(row, dict):
            continue
        at = row.get("at")
        if isinstance(at, int | float):
            fractions.append(float(at))
    return fractions or None


def table_columns(structure: dict[str, Any] | None) -> list[dict[str, Any]] | None:
    """The column titles of the form's first table."""
    table = _first_table(structure)
    if table is None:
        return None
    columns = [column for column in table.get("columns") or [] if isinstance(column, dict)]
    return columns or None
