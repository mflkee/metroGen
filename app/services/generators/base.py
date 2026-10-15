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
    #: Точки замера из структуры формы (доли ВПИ). Если заданы — генератор берёт их вместо своих.
    point_fractions: list[float] | None = None


def steps_from_fractions(fsv: float, fractions: list[float] | None) -> list[float] | None:
    """Пересчитать доли ВПИ из структуры формы в значения опорных точек."""
    if not fractions:
        return None
    steps: list[float] = []
    for fraction in fractions:
        try:
            steps.append(round(fsv * float(fraction), 1))
        except (TypeError, ValueError):
            continue
    return steps or None


class TableGenerator(Protocol):
    """Интерфейс любого генератора таблицы под конкретный «шаблон»."""

    def generate(self, gi: GenInput) -> dict[str, Any]: ...
