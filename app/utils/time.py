"""Московское время для отображения и дат по умолчанию."""

from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

MSK = ZoneInfo("Europe/Moscow")


def msk_now() -> datetime:
    return datetime.now(MSK)


def to_msk(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(MSK)


def msk_today() -> date:
    return msk_now().date()
