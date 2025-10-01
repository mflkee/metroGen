from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import select
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

    repo = MethodologyRepository(session)
    methodology = await repo.get_by_code(code)
    if methodology:
        return methodology

    seed_key, seed_payload = _match_seed(code)
    title = seed_payload.get("title_full") if seed_payload else code
    allowable = seed_payload.get("allowable_variation_pct") if seed_payload else None
    document = seed_payload.get("document") if seed_payload else None
    notes = seed_payload.get("notes") if seed_payload else None

    methodology = await repo.upsert_methodology(
        code=code,
        title=title or code,
        document=document,
        notes=notes,
        allowable_variation_pct=allowable,
    )

    await repo.ensure_aliases(
        methodology,
        [
            (code, 100),
            *(
                [(seed_key, 90)]
                if seed_key and normalize_methodology_alias(seed_key) != normalize_methodology_alias(code)
                else []
            ),
        ],
    )

    if seed_payload and seed_payload.get("points"):
        has_points = (
            await session.execute(
                select(models.MethodologyPoint.id).where(
                    models.MethodologyPoint.methodology_id == methodology.id
                ).limit(1)
            )
        ).scalar_one_or_none()
        if has_points:
            return await repo.get_by_code(code)
        points_payload = [
            MethodologyPointPayload(position=index, label=value)
            for index, (_, value) in enumerate(sorted(seed_payload["points"].items()), start=1)
        ]
        await repo.replace_points(methodology, points_payload)

    return await repo.get_by_code(code)


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
        for idx, point in enumerate(sorted(methodology.points, key=lambda p: (p.position, p.id or 0)), start=1)
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
