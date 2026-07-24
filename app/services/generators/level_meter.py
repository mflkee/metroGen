from __future__ import annotations

import math
from random import uniform

from .base import GenInput, TableGenerator


class LevelMeter(TableGenerator):
    """
    Генератор таблицы для уровнемеров:
      - равномерные точки 0..ВПИ
      - одно измерение на каждой точке (без прямого/обратного хода)
      - абсолютная и относительная погрешность
    """

    def generate(self, gi: GenInput) -> dict[str, object]:
        fsv = float(gi.range_max or 0.0)
        if fsv <= 0:
            return {
                "rows": [],
                "unit_label": gi.unit,
                "allowable_error": "",
                "allowable_variation": "",
            }

        n = max(int(gi.points or 5), 2)

        def _nice_steps(fsv: float, desired_points: int) -> list[float]:
            """Подбор равномерных опорных точек 0..FSV."""
            desired_intervals = max(desired_points - 1, 1)
            return [round((fsv * i) / desired_intervals, 6) for i in range(desired_points)]

        steps = _nice_steps(fsv, n)
        rows: list[dict[str, object]] = []

        for ref_val in steps:
            err_limit = gi.allowable_error.value(ref=ref_val, fsv=fsv, ctx=gi.ctx)

            err_pct = uniform(-err_limit * 0.6, err_limit * 0.6)
            err_pct = max(-err_limit, min(err_limit, err_pct))

            if abs(ref_val) < 1e-9:
                err_pct = 0.0

            si_val = ref_val + (err_pct / 100.0) * fsv
            abs_err = si_val - ref_val

            rows.append(
                {
                    "ref_val": _round_ref(ref_val),
                    "si_val": _round_si(si_val),
                    "abs_err": _round_err(abs_err),
                    "err_pct": _fmt_fixed(err_pct, 2),
                }
            )

        unit_label = gi.unit or ""
        disp_err = gi.allowable_error.value(ref=fsv, fsv=fsv, ctx=gi.ctx)

        return {
            "rows": rows,
            "unit_label": unit_label,
            "allowable_error": _fmt_tol(disp_err),
            "allowable_variation": "—",
        }


GENERATOR = LevelMeter()
TEMPLATE_ID = "level_meter"


def _round_si(x: float) -> str:
    return _fmt_fixed(x, 2)


def _round_ref(x: float) -> str:
    return _fmt_fixed(x, 3)


def _round_err(x: float) -> str:
    return _fmt_fixed(x, 3)


def _fmt_fixed(x: float, digits: int) -> str:
    try:
        x = float(x)
    except Exception:
        return ""
    threshold = 0.5 * (10 ** (-digits))
    if abs(x) < threshold:
        x = 0.0
    return f"{x:.{digits}f}"


def _fmt_tol(value: float) -> str:
    try:
        return f"{float(value):.2f}"
    except Exception:
        return str(value)
