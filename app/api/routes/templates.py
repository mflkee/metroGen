from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models import TemplateBindingRule
from app.schemas.template import (
    TemplatePreviewOut,
    TemplatePreviewRequest,
    TemplatePreviewStep,
    TemplateRuleCreate,
    TemplateRuleOut,
    TemplateRuleUpdate,
)
from app.services import template_rules
from app.services.templates import TEMPLATES

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


def _validate_rule_fields(
    *, instrument_kind: str | None, match_field: str | None, template_id: str | None
) -> None:
    if template_id is not None and template_id not in TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unknown template '{template_id}'",
        )
    if match_field is not None and match_field not in template_rules.MATCH_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unknown match_field '{match_field}'",
        )
    if instrument_kind is not None and instrument_kind not in template_rules.INSTRUMENT_KINDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unknown instrument_kind '{instrument_kind}'",
        )


@router.get("/rules", response_model=list[TemplateRuleOut], summary="List form mapping rules")
async def list_rules(session: AsyncSession = Depends(get_db)) -> list[TemplateRuleOut]:
    rows = (
        (
            await session.execute(
                select(TemplateBindingRule).order_by(
                    TemplateBindingRule.priority.asc(), TemplateBindingRule.id.asc()
                )
            )
        )
        .scalars()
        .all()
    )
    return [TemplateRuleOut.from_model(row) for row in rows]


@router.post(
    "/rules",
    response_model=TemplateRuleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a form mapping rule",
)
async def create_rule(
    payload: TemplateRuleCreate,
    session: AsyncSession = Depends(get_db),
) -> TemplateRuleOut:
    _validate_rule_fields(
        instrument_kind=payload.instrument_kind,
        match_field=payload.match_field,
        template_id=payload.template_id,
    )
    rule = TemplateBindingRule(
        instrument_kind=payload.instrument_kind.strip(),
        match_field=payload.match_field.strip(),
        match_value=payload.match_value.strip(),
        template_id=payload.template_id.strip(),
        priority=payload.priority,
        is_active=payload.is_active,
    )
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    template_rules.invalidate()
    return TemplateRuleOut.from_model(rule)


@router.patch(
    "/rules/{rule_id}",
    response_model=TemplateRuleOut,
    summary="Update a form mapping rule",
)
async def update_rule(
    rule_id: int,
    payload: TemplateRuleUpdate,
    session: AsyncSession = Depends(get_db),
) -> TemplateRuleOut:
    rule = await session.get(TemplateBindingRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="rule not found")

    _validate_rule_fields(
        instrument_kind=payload.instrument_kind,
        match_field=payload.match_field,
        template_id=payload.template_id,
    )

    if payload.instrument_kind is not None:
        rule.instrument_kind = payload.instrument_kind.strip()
    if payload.match_field is not None:
        rule.match_field = payload.match_field.strip()
    if payload.match_value is not None:
        rule.match_value = payload.match_value.strip()
    if payload.template_id is not None:
        rule.template_id = payload.template_id.strip()
    if payload.priority is not None:
        rule.priority = payload.priority
    if payload.is_active is not None:
        rule.is_active = payload.is_active

    await session.commit()
    await session.refresh(rule)
    template_rules.invalidate()
    return TemplateRuleOut.from_model(rule)


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a form mapping rule",
)
async def delete_rule(
    rule_id: int,
    session: AsyncSession = Depends(get_db),
) -> Response:
    rule = await session.get(TemplateBindingRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="rule not found")
    await session.delete(rule)
    await session.commit()
    template_rules.invalidate()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/rules/preview",
    response_model=TemplatePreviewOut,
    summary="Show which form a row resolves to, and why",
)
async def preview_rule(
    payload: TemplatePreviewRequest,
    session: AsyncSession = Depends(get_db),
) -> TemplatePreviewOut:
    resolution = await template_rules.resolve_form(
        session,
        method_code=payload.method_code,
        mitype_number=payload.mitype_number,
        mitype_title=payload.mitype_title,
        modification=payload.modification,
        instrument_kind=payload.instrument_kind,
        override=payload.override,
    )
    template_title = (TEMPLATES.get(resolution.template_id) or {}).get("title")
    return TemplatePreviewOut(
        template_id=resolution.template_id,
        template_title=str(template_title) if template_title else None,
        source=resolution.source,
        rule_id=resolution.rule_id,
        steps=[TemplatePreviewStep(**step) for step in resolution.steps],
    )
