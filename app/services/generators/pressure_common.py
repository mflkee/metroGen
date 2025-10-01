from __future__ import annotations

from random import uniform


def _fmt_fixed(x: float, digits: int) -> str:
    """Форматирование с устранением «-0.00» при очень малых значениях.

    Если |x| < 0.5*10^-digits — считаем это нулём.
    """
    try:
        x = float(x)
    except Exception:
        return ""  # на всякий случай
    threshold = 0.5 * (10 ** (-digits))
    if abs(x) < threshold:
        x = 0.0
    return f"{x:.{digits}f}"

from .base import GenInput, TableGenerator


def _round_si(x: float) -> str:  # показания СИ
    return _fmt_fixed(x, 2)


def _round_ref(x: float) -> str:  # показания эталона
    return _fmt_fixed(x, 3)


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

        def _nice_steps(fsv: float, desired_points: int) -> list[float]:
            """Подбор «красивых» опорных точек 0..FSV.

            Пытаемся найти шаг из ряда 1,2,5×10^k, чтобы FSV делился на шаг
            и число точек было близко к desired_points. Иначе — равномерно.
            """
            desired_intervals = max(desired_points - 1, 1)
            approx_step = fsv / desired_intervals

            candidates: list[float] = []
            for k in range(-4, 5):
                base = 10 ** k
                for b in (1.0, 2.0, 5.0):
                    candidates.append(b * base)

            best: tuple[float, int] | None = None
            best_score = float("inf")
            for s in candidates:
                if s <= 0:
                    continue
                m = fsv / s
                m_round = int(round(m))
                if m_round <= 0:
                    continue
                if abs(m - m_round) <= 1e-6:  # шаг кратен FSV
                    points = m_round + 1
                    score = abs(points - desired_points) + 0.1 * (abs(s - approx_step) / max(approx_step, 1e-9))
                    if score < best_score:
                        best = (s, points)
                        best_score = score

            if best:
                step, points = best
                return [round(i * step, 6) for i in range(points)]

            # Фоллбэк: равномерные точки
            return [round((fsv * i) / desired_intervals, 6) for i in range(desired_points)]

        steps = _nice_steps(fsv, n)
        rows: list[dict[str, object]] = []

        for i, ref_fwd in enumerate(steps):
            # Обратный ход — на той же опорной точке, что и прямой,
            # чтобы пары значений стояли в одной строке
            ref_rev = ref_fwd

            err_limit = gi.allowable_error.value(ref=ref_fwd, fsv=fsv, ctx=gi.ctx)
            # var_limit = gi.allowable_variation.value(
            #     ref=ref_fwd, fsv=fsv, ctx=gi.ctx
            # )  # для будущего

            err_fwd_pct = _clamp_err(uniform(-err_limit * 0.6, err_limit * 0.6), err_limit)
            err_rev_pct = _clamp_err(uniform(-err_limit * 0.6, err_limit * 0.6), err_limit)

            # На нулевой точке не допускаем «-0.00»/случайных знаков — считаем ровно 0
            if abs(ref_fwd) < 1e-9:
                err_fwd_pct = 0.0
            if abs(ref_rev) < 1e-9:
                err_rev_pct = 0.0

            si_fwd = ref_fwd + (err_fwd_pct / 100.0) * fsv
            si_rev = ref_rev + (err_rev_pct / 100.0) * fsv
            var_pct = abs(si_fwd - si_rev) / fsv * 100.0

            rows.append(
                {
                    "si_fwd": _round_si(si_fwd),
                    "si_rev": _round_si(si_rev),
                    "ref_fwd": _round_ref(ref_fwd),
                    "ref_rev": _round_ref(ref_rev),
                    "err_fwd": _fmt_fixed(err_fwd_pct, 2),
                    "err_rev": _fmt_fixed(err_rev_pct, 2),
                    "var_pct": _fmt_fixed(var_pct, 2),
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
