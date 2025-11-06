from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class OwnerCreate(BaseModel):
    name: str = Field(...)
    inn: str | None = Field(default=None)
    aliases: list[str] | None = None

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("name must not be empty")
        return text

    @field_validator("inn")
    @classmethod
    def _strip_inn(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        return text or None


class OwnerUpdate(BaseModel):
    name: str | None = Field(default=None)
    inn: str | None = Field(default=None)
    aliases: list[str] | None = None

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        if not text:
            raise ValueError("name must not be empty")
        return text

    @field_validator("inn")
    @classmethod
    def _strip_inn(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        return text or None


class OwnerOut(BaseModel):
    id: int
    name: str
    inn: str | None = None

    @classmethod
    def from_model(cls, owner: Any) -> OwnerOut:
        return cls(id=owner.id, name=owner.name, inn=owner.inn)
