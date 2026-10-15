from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser, get_db
from app.db.models import ProtocolForm, ProtocolFormVersion, TemplateBindingRule
from app.schemas.template import (
    TemplateCatalogOut,
    TemplateFormDetailOut,
    TemplateOut,
    TemplatePreviewOut,
    TemplatePreviewRenderOut,
    TemplatePreviewRequest,
    TemplatePreviewStep,
    TemplatePublishRequest,
    TemplateRuleBriefOut,
    TemplateRuleCreate,
    TemplateRuleOut,
    TemplateRuleUpdate,
    TemplateStructureUpdate,
    TemplateVersionOut,
)
from app.services import form_structure, template_rules
from app.services.templates import TEMPLATES

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


# A form as the catalogue needs it. Rows come from `protocol_forms`; when that table is missing
# (an older database, a test run without migrations) the catalogue falls back to the static
# registry, so the endpoint never breaks.
@dataclass(frozen=True)
class _FormView:
    code: str
    title: str
    instrument_kind: str
    parent_code: str | None
    renderer: str
    is_active: bool
    notes: str | None = None


_FALLBACK_KIND_BY_PREFIX: tuple[tuple[str, str], ...] = (
    ("pressure_", "manometers"),
    ("controller_", "controllers"),
    ("rtd_", "thermometers"),
    ("level_meter", "level_meters"),
)

_FALLBACK_PARENTS: dict[str, str] = {
    "level_meter_two_tables": "level_meter",
    "level_meter_current_output": "level_meter",
}


def _fallback_kind(code: str) -> str:
    for prefix, kind in _FALLBACK_KIND_BY_PREFIX:
        if code.startswith(prefix):
            return kind
    return "manometers"


def _fallback_forms() -> list[_FormView]:
    return [
        _FormView(
            code=code,
            title=str(tpl.get("title") or code),
            instrument_kind=_fallback_kind(code),
            parent_code=_FALLBACK_PARENTS.get(code),
            renderer="html",
            is_active=True,
        )
        for code, tpl in TEMPLATES.items()
    ]


async def _load_forms(session: AsyncSession) -> list[_FormView]:
    try:
        rows = (
            (
                await session.execute(
                    select(ProtocolForm).order_by(
                        ProtocolForm.instrument_kind.asc(), ProtocolForm.code.asc()
                    )
                )
            )
            .scalars()
            .all()
        )
    except Exception:
        return _fallback_forms()

    if not rows:
        return _fallback_forms()

    return [
        _FormView(
            code=row.code,
            title=row.title,
            instrument_kind=row.instrument_kind,
            parent_code=row.parent_code,
            renderer=row.renderer,
            is_active=row.is_active,
            notes=row.notes,
        )
        for row in rows
    ]


def _children_map(forms: list[_FormView]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = {}
    for form in forms:
        if form.parent_code:
            children.setdefault(form.parent_code, []).append(form.code)
    return children


def _to_out(form: _FormView, children: dict[str, list[str]]) -> TemplateOut:
    return TemplateOut(
        id=form.code,
        title=form.title,
        instrument_kind=form.instrument_kind,
        parent_code=form.parent_code,
        children=sorted(children.get(form.code, [])),
        renderer=form.renderer,
        is_active=form.is_active,
        is_editable=True,
        drives_protocol=form.renderer == "data",
    )


async def _load_form_rows(session: AsyncSession) -> dict[str, ProtocolForm]:
    """ORM rows by code — the write endpoints and the structure resolver need the real rows."""
    try:
        rows = (await session.execute(select(ProtocolForm))).scalars().all()
    except Exception:
        return {}
    return {row.code: row for row in rows}


def _version_out(version: ProtocolFormVersion) -> TemplateVersionOut:
    published_at = getattr(version, "published_at", None)
    return TemplateVersionOut(
        revision=version.revision,
        comment=version.comment,
        published_by=version.published_by,
        published_at=published_at.isoformat() if published_at else None,
        overlay=dict(version.overlay or {}),
        structure_resolved=dict(version.structure_resolved or {}),
    )


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


@router.get("", response_model=TemplateCatalogOut, summary="List protocol forms and rule options")
async def list_templates(session: AsyncSession = Depends(get_db)) -> TemplateCatalogOut:
    forms = await _load_forms(session)
    children = _children_map(forms)
    return TemplateCatalogOut(
        templates=[
            _to_out(form, children)
            for form in sorted(forms, key=lambda item: (item.instrument_kind, item.code))
        ],
        instrument_kinds=list(template_rules.INSTRUMENT_KINDS),
        match_fields=list(template_rules.MATCH_FIELDS),
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
async def delete_rule(rule_id: int, session: AsyncSession = Depends(get_db)) -> Response:
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


# Declared last: `/rules` and `/rules/...` must win over the `{form_code}` catch-all.
@router.get(
    "/{form_code}",
    response_model=TemplateFormDetailOut,
    summary="A form with the rules that select it",
)
async def get_template(
    form_code: str, session: AsyncSession = Depends(get_db)
) -> TemplateFormDetailOut:
    forms = await _load_forms(session)
    form = next((item for item in forms if item.code == form_code), None)
    if form is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="form not found")

    rows = (
        (
            await session.execute(
                select(TemplateBindingRule)
                .where(TemplateBindingRule.template_id == form_code)
                .order_by(TemplateBindingRule.priority.asc(), TemplateBindingRule.id.asc())
            )
        )
        .scalars()
        .all()
    )
    rows_by_code = await _load_form_rows(session)
    resolved = form_structure.resolve_structure(form_code, rows_by_code)
    own_row = rows_by_code.get(form_code)
    overlay = dict(getattr(own_row, "overlay", None) or {})

    return TemplateFormDetailOut(
        form=_to_out(form, _children_map(forms)),
        rules=[
            TemplateRuleBriefOut(
                id=row.id,
                instrument_kind=row.instrument_kind,
                match_field=row.match_field,
                match_value=row.match_value,
                priority=row.priority,
                is_active=row.is_active,
            )
            for row in rows
        ],
        structure=resolved,
        overlay=overlay,
        overlay_keys=form_structure.overlay_keys(overlay),
        problems=form_structure.validate_structure(resolved) if resolved else [],
    )


@router.put(
    "/{form_code}/draft",
    response_model=TemplateFormDetailOut,
    summary="Save a draft of a form's structure (administrators)",
)
async def save_form_draft(
    form_code: str,
    payload: TemplateStructureUpdate,
    user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> TemplateFormDetailOut:
    row = (await _load_form_rows(session)).get(form_code)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="form not found")

    if payload.structure is not None:
        problems = form_structure.validate_structure(payload.structure)
        if problems:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "structure is invalid", "problems": problems},
            )
        row.structure = payload.structure
    if payload.overlay is not None:
        row.overlay = payload.overlay

    await session.commit()
    return await get_template(form_code, session)


@router.post(
    "/{form_code}/publish",
    response_model=TemplateVersionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Publish the current draft as a new version (administrators)",
)
async def publish_form(
    form_code: str,
    payload: TemplatePublishRequest,
    user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> TemplateVersionOut:
    rows_by_code = await _load_form_rows(session)
    row = rows_by_code.get(form_code)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="form not found")

    resolved = form_structure.resolve_structure(form_code, rows_by_code)
    problems = form_structure.validate_structure(resolved)
    if problems:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "structure is invalid", "problems": problems},
        )

    last_revision = (
        await session.execute(
            select(func.max(ProtocolFormVersion.revision)).where(
                ProtocolFormVersion.form_id == row.id
            )
        )
    ).scalar() or 0

    version = ProtocolFormVersion(
        form_id=row.id,
        revision=int(last_revision) + 1,
        structure_resolved=resolved,
        overlay=dict(row.overlay or {}),
        comment=(payload.comment or "").strip() or None,
        published_by=getattr(user, "email", None),
    )
    session.add(version)
    await session.commit()
    await session.refresh(version)
    return _version_out(version)


@router.get(
    "/{form_code}/versions",
    response_model=list[TemplateVersionOut],
    summary="List the published versions of a form",
)
async def list_form_versions(
    form_code: str, session: AsyncSession = Depends(get_db)
) -> list[TemplateVersionOut]:
    row = (await _load_form_rows(session)).get(form_code)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="form not found")

    versions = (
        (
            await session.execute(
                select(ProtocolFormVersion)
                .where(ProtocolFormVersion.form_id == row.id)
                .order_by(ProtocolFormVersion.revision.desc())
            )
        )
        .scalars()
        .all()
    )
    return [_version_out(version) for version in versions]


@router.post(
    "/{form_code}/versions/{revision}/restore",
    response_model=TemplateVersionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Restore a published version as a new one (administrators)",
)
async def restore_form_version(
    form_code: str,
    revision: int,
    user: AdminUser,
    session: AsyncSession = Depends(get_db),
) -> TemplateVersionOut:
    row = (await _load_form_rows(session)).get(form_code)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="form not found")

    source = (
        await session.execute(
            select(ProtocolFormVersion).where(
                ProtocolFormVersion.form_id == row.id,
                ProtocolFormVersion.revision == revision,
            )
        )
    ).scalar_one_or_none()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="version not found")

    row.overlay = dict(source.overlay or {})
    last_revision = (
        await session.execute(
            select(func.max(ProtocolFormVersion.revision)).where(
                ProtocolFormVersion.form_id == row.id
            )
        )
    ).scalar() or 0

    version = ProtocolFormVersion(
        form_id=row.id,
        revision=int(last_revision) + 1,
        structure_resolved=dict(source.structure_resolved or {}),
        overlay=dict(source.overlay or {}),
        comment=f"restore of revision {revision}",
        published_by=getattr(user, "email", None),
    )
    session.add(version)
    await session.commit()
    await session.refresh(version)
    return _version_out(version)


@router.post(
    "/{form_code}/preview",
    response_model=TemplatePreviewRenderOut,
    summary="Render the draft structure of a form",
)
async def preview_form_structure(
    form_code: str, session: AsyncSession = Depends(get_db)
) -> TemplatePreviewRenderOut:
    rows_by_code = await _load_form_rows(session)
    if form_code not in rows_by_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="form not found")
    resolved = form_structure.resolve_structure(form_code, rows_by_code)
    return TemplatePreviewRenderOut(html=form_structure.render_structure_preview(resolved))
