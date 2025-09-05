from __future__ import annotations

from random import uniform

from .base import GenInput, TableGenerator


def _round_si(x: float) -> str:  # показания СИ
    return f"{x:.2f}"


def _round_ref(x: float) -> str:  # показания эталона
    return f"{x:.3f}"


def _clamp_err(pct: float, limit_pct: float) -> float:
    """Ограничить случайную ошибку по модулю допустимым значением."""
    lim = abs(float(limit_pct))
    p = float(pct)
    if abs(p) <= lim:
        return p
    return (lim if p > 0 else -lim) * uniform(0.70, 0.95)


class PressureCommon(TableGenerator):
    """
    Общий генератор для манометров:
      - равномерные точки 0..ВПИ
      - прямой/обратный ход на одних опорных точках
      - ошибки и вариация «внутри» допусков (отображаем допуски отдельно)
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

        n = max(int(gi.points or 8), 2)
        steps = [round((fsv * i) / (n - 1), 3) for i in range(n)]
        rows: list[dict[str, object]] = []

        for i, ref_fwd in enumerate(steps):
            ref_rev = steps[-(i + 1)]

            err_limit = gi.allowable_error.value(ref=ref_fwd, fsv=fsv, ctx=gi.ctx)
            # var_limit = gi.allowable_variation.value(
            #     ref=ref_fwd, fsv=fsv, ctx=gi.ctx
            # )  # для будущего

            err_fwd_pct = _clamp_err(uniform(-err_limit * 0.6, err_limit * 0.6), err_limit)
            err_rev_pct = _clamp_err(uniform(-err_limit * 0.6, err_limit * 0.6), err_limit)

            si_fwd = ref_fwd + (err_fwd_pct / 100.0) * fsv
            si_rev = ref_rev + (err_rev_pct / 100.0) * fsv
            var_pct = abs(si_fwd - si_rev) / fsv * 100.0

            rows.append(
                {
                    "si_fwd": _round_si(si_fwd),
                    "si_rev": _round_si(si_rev),
                    "ref_fwd": _round_ref(ref_fwd),
                    "ref_rev": _round_ref(ref_rev),
                    "err_fwd": f"{err_fwd_pct:.2f}",
                    "err_rev": f"{err_rev_pct:.2f}",
                    "var_pct": f"{var_pct:.2f}",
                }
            )

        unit_label = (gi.unit or "").replace("кгc", "кгс")
        disp_err = gi.allowable_error.value(ref=fsv, fsv=fsv, ctx=gi.ctx)
        disp_var = gi.allowable_variation.value(ref=fsv, fsv=fsv, ctx=gi.ctx)

        return {
            "rows": rows,
            "unit_label": unit_label,
            "allowable_error": f"{disp_err:.2f}",
            "allowable_variation": f"{disp_var:.2f}",
        }


GENERATOR = PressureCommon()
TEMPLATE_ID = "pressure_common"
