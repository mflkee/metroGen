from __future__ import annotations

import logging
from random import uniform

from .base import GenInput, TableGenerator

logger = logging.getLogger(__name__)


class LevelMeter(TableGenerator):
    """
    Генератор таблицы для уровнемеров.

    Ключевое отличие от манометров: погрешность задаётся в мм абсолютно,
    а не в процентах от ВПИ.

    Подтипы (по mitype_number из gi.ctx):
      - 86065-22 (Insol 90X)          → две таблицы: А.1 (жидкие) + А.2 (раздел)
      - 47249-16 (Levelflex FMP51)   → таблица мм + токовый выход мА
      - остальные                    → одна таблица мм
    """

    def generate(self, gi: GenInput) -> dict[str, object]:
        fsv = float(gi.range_max or 0.0)
        if fsv <= 0:
            logger.warning(
                "level_meter: fsv=%s (range_max=%s) — returning empty rows", fsv, gi.range_max
            )
            return {
                "rows": [],
                "unit_label": "мм",
                "allowable_error": "",
                "allowable_variation": "",
            }

        ctx = gi.ctx or {}
        mitype_number = str(ctx.get("mitype_number") or "").strip()

        n = max(int(gi.points or 5), 2)

        # Допуск в мм (абсолютный, не %).
        # Для уровнемеров gi.allowable_error.value() возвращает число мм
        # (например 5.0), а не процент.
        err_limit_mm = gi.allowable_error.value(ref=fsv, fsv=fsv, ctx=ctx)
        try:
            err_limit_mm = float(err_limit_mm)
        except Exception:
            err_limit_mm = 5.0

        steps = _nice_steps(fsv, n)
        rows: list[dict[str, object]] = []

        for ref_val in steps:
            # Случайная погрешность в пределах допуска (с запасом 60%)
            err_mm = uniform(-err_limit_mm * 0.6, err_limit_mm * 0.6)
            err_mm = max(-err_limit_mm, min(err_limit_mm, err_mm))

            # На нуле — ровно 0
            if abs(ref_val) < 1e-9:
                err_mm = 0.0

            si_val = ref_val + err_mm
            abs_err = si_val - ref_val

            rows.append(
                {
                    "si_val": _round_val(si_val),
                    "ref_val": _round_val(ref_val),
                    "abs_err": _round_err(abs_err),
                    "allowable_error": _fmt_allowable(err_limit_mm),
                }
            )

        result: dict[str, object] = {
            "rows": rows,
            "unit_label": "мм",
            "allowable_error": _fmt_allowable(err_limit_mm),
            "allowable_variation": "",
        }

        # === Insol 86065-22 — вторая таблица (раздела сред) ===
        if mitype_number == "86065-22":
            rows_b: list[dict[str, object]] = []
            for ref_val in steps:
                err_mm = uniform(-err_limit_mm * 0.6, err_limit_mm * 0.6)
                err_mm = max(-err_limit_mm, min(err_limit_mm, err_mm))
                if abs(ref_val) < 1e-9:
                    err_mm = 0.0
                si_val = ref_val + err_mm
                abs_err = si_val - ref_val
                rows_b.append(
                    {
                        "si_val": _round_val(si_val),
                        "ref_val": _round_val(ref_val),
                        "abs_err": _round_err(abs_err),
                        "allowable_error": _fmt_allowable(err_limit_mm),
                    }
                )
            result["table_rows_b"] = rows_b
            result["insol_two_tables"] = True

        # === Levelflex FMP51 47249-16 — токовый выход мА ===
        if mitype_number == "47249-16":
            current_output_rows = [
                {
                    "si_val": "4",
                    "ref_val": "4",
                    "abs_err": "0",
                    "allowable": "±0,25 мА",
                },
                {
                    "si_val": "12",
                    "ref_val": "12",
                    "abs_err": "0",
                    "allowable": "±0,25 мА",
                },
                {
                    "si_val": _fmt_current(20.0 + uniform(-0.15, 0.15)),
                    "ref_val": "20",
                    "abs_err": _fmt_current(uniform(-0.15, 0.15)),
                    "allowable": "±0,25 мА",
                },
            ]
            result["has_current_output_table"] = True
            result["current_output_rows"] = current_output_rows

        return result


GENERATOR = LevelMeter()
TEMPLATE_ID = "level_meter"


def _nice_steps(fsv: float, desired_points: int) -> list[float]:
    """Равномерные опорные точки 0..FSV."""
    desired_intervals = max(desired_points - 1, 1)
    return [round((fsv * i) / desired_intervals, 1) for i in range(desired_points)]


def _round_val(x: float) -> str:
    return _fmt_fixed(x, 1)


def _round_err(x: float) -> str:
    return _fmt_fixed(x, 1)


def _fmt_fixed(x: float, digits: int) -> str:
    try:
        x = float(x)
    except Exception:
        return ""
    threshold = 0.5 * (10 ** (-digits))
    if abs(x) < threshold:
        x = 0.0
    return f"{x:.{digits}f}"


def _fmt_allowable(value: float) -> str:
    try:
        v = float(value)
        # Округляем до целого если близко
        if abs(v - round(v)) < 0.01:
            return f"±{int(round(v))} мм"
        return f"±{v:.1f} мм"
    except Exception:
        return str(value)


def _fmt_current(x: float) -> str:
    try:
        x = float(x)
        if abs(x) < 0.001:
            x = 0.0
        return f"{x:.3f}"
    except Exception:
        return str(x)
