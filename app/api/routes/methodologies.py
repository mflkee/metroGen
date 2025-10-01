from __future__ import annotations

import re
from collections.abc import Iterable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import MethodologyPointType
from app.db.repositories import MethodologyPointPayload, MethodologyRepository
from app.schemas.methodology import (
    MethodologyCreate,
    MethodologyOut,
    MethodologyPointIn,
)

router = APIRouter(prefix="/api/v1/methodologies", tags=["methodologies"])


def _infer_point_type(payload: MethodologyPointIn) -> MethodologyPointType:
    if payload.point_type:
        return payload.point_type

    label = payload.label.strip().lower()
    if "____" in label or "__" in label:
        return MethodologyPointType.CUSTOM

    if "соответствует" in label:
        if "не соответствует" in label or "соответствует/не соответствует" in label:
            return MethodologyPointType.BOOL
        return MethodologyPointType.BOOL

    return MethodologyPointType.CLAUSE


def _strip_label(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    return cleaned


def _payload_points(points: Iterable[MethodologyPointIn]) -> list[MethodologyPointPayload]:
    payload: list[MethodologyPointPayload] = []
    for point in points:
        label = _strip_label(point.label)
        if not label:
            continue
        payload.append(
            MethodologyPointPayload(
                position=point.position,
                label=label,
                point_type=_infer_point_type(point),
            )
        )
    return payload


@router.post("", response_model=MethodologyOut, status_code=201)
async def create_methodology(
    body: MethodologyCreate,
    session: AsyncSession = Depends(get_db),
) -> MethodologyOut:
    if not body.points:
        raise HTTPException(status_code=400, detail="points are required")

    repo = MethodologyRepository(session)
    methodology = await repo.upsert_methodology(
        code=body.code,
        title=body.title or body.code,
        document=body.document,
        notes=body.notes,
        allowable_variation_pct=body.allowable_variation_pct,
    )

    alias_payload = [(body.code, 100)]
    if body.title and body.title != body.code:
        alias_payload.append((body.title, 90))
    for alias in body.aliases:
        alias_payload.append((alias, 80))

    await repo.ensure_aliases(methodology, alias_payload)

    payload_points = _payload_points(body.points)
    if not payload_points:
        raise HTTPException(status_code=400, detail="at least one point must have non-empty label")

    await repo.replace_points(methodology, payload_points)
    await session.commit()

    refreshed = await repo.get_by_code(body.code)
    if refreshed is None:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="failed to load methodology")

    return MethodologyOut.from_orm_obj(refreshed)
