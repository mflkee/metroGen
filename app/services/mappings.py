from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.repositories import (
    MethodologyPointPayload,
    MethodologyRepository,
    OwnerRepository,
)
from app.db.repositories.utils import normalize_methodology_alias

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(slots=True)
class MethodologyInfo:
    code: str
    title: str
    allowable_variation_pct: float | None
    points: dict[str, str]


def _sanitize_methodology_code(value: str | None) -> str:
    """Trim methodology identifiers to fit DB constraints."""
    if not value:
        return ""

    text = value.strip()
    text = text.strip('" ')
    text = text.strip("«»")
    if len(text) <= 128 and text:
        return text

    shortened = text[:128].rstrip(" ,;")
    return shortened or text[:128]


@lru_cache(maxsize=1)
def _methodology_seed() -> dict[str, Any]:
    path = DATA_DIR / "methodologies.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _org_seed() -> dict[str, Any]:
    path = DATA_DIR / "orgs.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _core_code(text: str) -> str:
    m = re.search(r"(\d{3,5}-\d{2})", text.replace(" ", ""))
    return m.group(1) if m else text


def _match_seed(code: str) -> tuple[str, dict[str, Any]] | tuple[None, None]:
    data = _methodology_seed()
    if code in data:
        return code, data[code]
    core = _core_code(code)
    for key, payload in data.items():
        if _core_code(key) == core:
            return key, payload
    lowered = code.lower()
    for key, payload in data.items():
        if key in code or key.lower() in lowered:
            return key, payload
    return None, None


async def ensure_owner(
    session: AsyncSession,
    name: str | None,
    *,
    inn_hint: str | None = None,
    aliases: Iterable[str] | None = None,
) -> models.Owner | None:
    if not name:
        return None

    repo = OwnerRepository(session)
    owner = await repo.get_by_alias(name)
    if owner is None:
        owner = await repo.get_by_name(name)

    if owner is None:
        fallback_inn = inn_hint or (_org_seed().get(name) or {}).get("inn")
        owner = models.Owner(name=name, inn=fallback_inn)
        await repo.add(owner)
    else:
        if inn_hint and owner.inn != inn_hint:
            owner.inn = inn_hint

    alias_values = list(aliases or [])
    if name not in alias_values:
        alias_values.append(name)
    if alias_values:
        await repo.ensure_aliases(owner, alias_values)
    return owner


async def resolve_owner_inn(session: AsyncSession, name: str | None) -> str | None:
    owner = await ensure_owner(session, name)
    return owner.inn if owner else None


async def ensure_methodology(
    session: AsyncSession,
    code: str | None,
) -> models.Methodology | None:
    if not code:
        return None

    sanitized_code = _sanitize_methodology_code(code)
    repo = MethodologyRepository(session)

    for candidate in (code, sanitized_code):
        if not candidate:
            continue
        methodology = await repo.get_by_code(candidate)
        if methodology:
            return methodology
        methodology = await repo.get_by_alias(candidate)
        if methodology:
            return methodology

    normalized = normalize_methodology_alias(code)
    if normalized:
        normalized_compact = normalized.replace(" и ", " ")
        alias_compact = func.replace(models.MethodologyAlias.normalized_alias, " и ", " ")
        stmt = (
            select(models.Methodology)
            .join(models.MethodologyAlias)
            .where(
                or_(
                    func.strpos(normalized_compact, alias_compact) > 0,
                    func.strpos(alias_compact, normalized_compact) > 0,
                )
            )
            .order_by(func.length(models.MethodologyAlias.normalized_alias).desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        methodology = result.unique().scalar_one_or_none()
        if methodology:
            return methodology

    seed_key, seed_payload = _match_seed(sanitized_code or code)
    title = seed_payload.get("title_full") if seed_payload else code
    allowable = seed_payload.get("allowable_variation_pct") if seed_payload else None
    document = seed_payload.get("document") if seed_payload else None
    notes = seed_payload.get("notes") if seed_payload else None

    store_code = sanitized_code or code[:128].strip()
    if not store_code:
        return None

    methodology = await repo.upsert_methodology(
        code=store_code,
        title=title or code,
        document=document,
        notes=notes,
        allowable_variation_pct=allowable,
    )

    alias_candidates: list[tuple[str, int]] = [(store_code, 100)]
    if code and code != store_code:
        alias_candidates.append((code, 90))
    if seed_key and normalize_methodology_alias(seed_key) != normalize_methodology_alias(store_code):
        alias_candidates.append((seed_key, 85))
    await repo.ensure_aliases(methodology, alias_candidates)

    if seed_payload and seed_payload.get("points"):
        has_points = (
            await session.execute(
                select(models.MethodologyPoint.id)
                .where(models.MethodologyPoint.methodology_id == methodology.id)
                .limit(1)
            )
        ).scalar_one_or_none()
        if has_points:
            return await repo.get_by_code(store_code)
        points_payload = [
            MethodologyPointPayload(position=index, label=value)
            for index, (_, value) in enumerate(sorted(seed_payload["points"].items()), start=1)
        ]
        await repo.replace_points(methodology, points_payload)

    return await repo.get_by_code(store_code)


async def resolve_methodology(
    session: AsyncSession,
    code: str | None,
) -> MethodologyInfo | None:
    if not code:
        return None

    methodology = await ensure_methodology(session, code)
    if methodology is None:
        return None

    # ensure relationships are loaded (selectinload in repository handles existing ones)
    points = {
        f"p{idx}": point.label
        for idx, point in enumerate(
            sorted(methodology.points, key=lambda p: (p.position, p.id or 0)), start=1
        )
    }

    return MethodologyInfo(
        code=methodology.code,
        title=methodology.title or methodology.code,
        allowable_variation_pct=methodology.allowable_variation_pct,
        points=points,
    )


async def resolve_owner_and_inn(
    session: AsyncSession,
    name: str | None,
    *,
    inn_hint: str | None = None,
) -> tuple[str | None, str | None]:
    owner = await ensure_owner(session, name, inn_hint=inn_hint)
    if owner is None:
        return name, inn_hint
    return owner.name, owner.inn
