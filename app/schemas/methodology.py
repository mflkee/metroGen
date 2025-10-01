from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.db.models import MethodologyPointType


class MethodologyPointIn(BaseModel):
    position: int = Field(..., ge=1)
    label: str = Field(..., min_length=1)
    point_type: MethodologyPointType | None = None


class MethodologyCreate(BaseModel):
    code: str = Field(..., min_length=1)
    title: str | None = None
    document: str | None = None
    notes: str | None = None
    allowable_variation_pct: float | None = Field(None, ge=0)
    aliases: list[str] = Field(default_factory=list)
    points: list[MethodologyPointIn] = Field(default_factory=list)


class MethodologyPointOut(BaseModel):
    position: int
    label: str
    point_type: MethodologyPointType


class MethodologyOut(BaseModel):
    code: str
    title: str
    document: str | None
    notes: str | None
    allowable_variation_pct: float | None
    points: list[MethodologyPointOut]

    @classmethod
    def from_orm_obj(cls, obj: Any) -> MethodologyOut:
        points = [
            MethodologyPointOut(
                position=point.position,
                label=point.label,
                point_type=MethodologyPointType(point.point_type),
            )
            for point in sorted(obj.points, key=lambda p: (p.position, p.id or 0))
        ]
        return cls(
            code=obj.code,
            title=obj.title,
            document=obj.document,
            notes=obj.notes,
            allowable_variation_pct=obj.allowable_variation_pct,
            points=points,
        )
