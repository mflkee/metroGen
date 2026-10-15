from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class Tolerance(Protocol):
    """Интерфейс допуска, возвращает допустимое значение (в процентах)."""

    def value(self, *, ref: float, fsv: float, ctx: dict[str, Any]) -> float: ...


@dataclass
class FixedPctTol:
    """Постоянный допуск, %."""

    pct: float

    def value(self, *, ref: float, fsv: float, ctx: dict[str, Any]) -> float:
        return float(self.pct)


@dataclass
class GenInput:
    """Вход генератора таблицы."""

    range_min: float
    range_max: float
    unit: str
    points: int
    allowable_error: Tolerance
    allowable_variation: Tolerance
    ctx: dict[str, Any]


class TableGenerator(Protocol):
    """Интерфейс любого генератора таблицы под конкретный «шаблон»."""

    def generate(self, gi: GenInput) -> dict[str, Any]: ...
