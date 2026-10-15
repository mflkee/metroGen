from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TemplateRuleOut(BaseModel):
    id: int
    instrument_kind: str
    match_field: str
    match_value: str
    template_id: str
    priority: int
    is_active: bool

    @classmethod
    def from_model(cls, rule: Any) -> TemplateRuleOut:
        return cls(
            id=rule.id,
            instrument_kind=rule.instrument_kind,
            match_field=rule.match_field,
            match_value=rule.match_value,
            template_id=rule.template_id,
            priority=rule.priority,
            is_active=rule.is_active,
        )


class TemplateRuleCreate(BaseModel):
    instrument_kind: str = Field(..., min_length=1)
    match_field: str = Field(..., min_length=1)
    match_value: str = Field(..., min_length=1)
    template_id: str = Field(..., min_length=1)
    priority: int = 100
    is_active: bool = True


class TemplateRuleUpdate(BaseModel):
    instrument_kind: str | None = None
    match_field: str | None = None
    match_value: str | None = None
    template_id: str | None = None
    priority: int | None = None
    is_active: bool | None = None


class TemplatePreviewRequest(BaseModel):
    instrument_kind: str | None = None
    method_code: str | None = None
    mitype_number: str | None = None
    mitype_title: str | None = None
    modification: str | None = None
    override: str | None = None


class TemplatePreviewStep(BaseModel):
    stage: str
    matched: bool
    rule_id: int | None = None
    match_field: str | None = None
    match_value: str | None = None
    methodology_code: str | None = None
    template_id: str | None = None


class TemplatePreviewOut(BaseModel):
    template_id: str
    template_title: str | None = None
    source: str
    rule_id: int | None = None
    steps: list[TemplatePreviewStep] = Field(default_factory=list)
