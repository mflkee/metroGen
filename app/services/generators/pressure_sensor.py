from __future__ import annotations

from random import uniform

from .base import GenInput, TableGenerator

# Датчики/преобразователи давления с унифицированным токовым выходом 4–20 мА.
BASE_MA: float = 4.0
SPAN_MA: float = 16.0


def _fmt_fixed(x: float, digits: int) -> str:
    """Форматирование с устранением «-0.000» при очень малых значениях."""
    try:
        x = float(x)
    except Exception:
        return ""
    threshold = 0.5 * (10 ** (-digits))
    if abs(x) < threshold:
        x = 0.0
    return f"{x:.{digits}f}"


def _fmt_trim(x: float) -> str:
    """Давление без хвостовых нулей (0, 6.25, 12.5, 18.75, 25)."""
    try:
        x = float(x)
    except Exception:
        return ""
    if abs(x) < 1e-9:
        return "0"
    return f"{x:.3f}".rstrip("0").rstrip(".")


def _fmt_pct(value: float) -> str:
    return f"{float(value):g}"


class PressureSensor(TableGenerator):
    """Таблица для датчиков давления (токовый выход через калибратор).

    В отличие от манометров, задаётся давление и измеряется выходной сигнал (мА):
      - 5 точек 0..ВПИ (0/25/50/75/100 %),
      - номинальный сигнал 4..20 мА,
      - измеренный сигнал прямым/обратным ходом,
      - приведённая погрешность относительно диапазона 16 мА,
      - вариация выходного сигнала γ.
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
        steps = [fsv * i / (n - 1) for i in range(n)]

        allowable_pct = float(
            gi.allowable_error.value(ref=fsv, fsv=fsv, ctx=gi.ctx)
        )
        allowable_ma = abs(allowable_pct) / 100.0 * SPAN_MA
        variation_ma = allowable_ma * 0.5

        rows: list[dict[str, str]] = []
        for ref in steps:
            nominal = BASE_MA + SPAN_MA * (ref / fsv)

            err_f = uniform(-allowable_ma * 0.7, allowable_ma * 0.7)
            err_r = uniform(-allowable_ma * 0.7, allowable_ma * 0.7)
            # Вариация выходного сигнала не выходит за допустимую вариацию.
            if variation_ma > 0 and abs(err_f - err_r) > variation_ma:
                err_r = err_f + (variation_ma if err_r >= err_f else -variation_ma)

            meas_f = nominal + err_f
            meas_r = nominal + err_r

            rows.append(
                {
                    "pressure": _fmt_trim(ref),
                    "nominal_ma": _fmt_fixed(nominal, 3),
                    "meas_fwd": _fmt_fixed(meas_f, 3),
                    "meas_rev": _fmt_fixed(meas_r, 3),
                    "err_fwd": _fmt_fixed((meas_f - nominal) / SPAN_MA * 100.0, 3),
                    "err_rev": _fmt_fixed((meas_r - nominal) / SPAN_MA * 100.0, 3),
                    "variation": _fmt_fixed((meas_f - meas_r) / SPAN_MA * 100.0, 3),
                }
            )

        return {
            "rows": rows,
            "unit_label": (gi.unit or "").replace("кгc", "кгс"),
            "allowable_error": _fmt_pct(allowable_pct),
            "allowable_variation": _fmt_pct(allowable_pct),
        }


GENERATOR = PressureSensor()
TEMPLATE_ID = "pressure_sensor"
