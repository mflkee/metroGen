from __future__ import annotations

from random import uniform
from statistics import mean

from .base import GenInput, TableGenerator

_TARGET_POINTS = (
    (0.0, 100.0),  # (temperature °C, nominal resistance Ω)
    (100.0, 138.51),
)

_ALLOWABLE_BY_POINT = {
    0.0: 0.06,  # Ом для точки 0 °C (класс А, приближенно)
    100.0: 0.13,  # Ом для точки 100 °C
}

_ALPHA = 0.00385  # температурный коэффициент для Pt100
_MEASUREMENTS_PER_POINT = 4


def _fmt(value: float, digits: int = 3) -> str:
    try:
        value = float(value)
    except Exception:
        return ""
    text = f"{value:.{digits}f}"
    # устраняем -0.000
    if text.lstrip("-").startswith("0." + "0" * digits):
        text = text.replace("-0", "0", 1)
    return text.rstrip("0").rstrip(".") if "." in text else text


class RTDGenerator(TableGenerator):
    """
    Генератор таблицы для термопреобразователей сопротивления:
    фиксированные точки 0 и 100 °C, для каждой — 4 измерения и усреднение.
    """

    def generate(self, gi: GenInput) -> dict[str, object]:
        groups: list[dict[str, object]] = []
        flat_rows: list[dict[str, str]] = []

        base_r0 = _TARGET_POINTS[0][1]

        for temp, nominal_res in _TARGET_POINTS:
            allowable = _ALLOWABLE_BY_POINT.get(
                temp,
                gi.allowable_error.value(ref=nominal_res, fsv=gi.range_max, ctx=gi.ctx),
            )

            measurements: list[dict[str, str]] = []
            measured_res_raw: list[float] = []
            measured_temp_raw: list[float] = []

            for meas_idx in range(1, _MEASUREMENTS_PER_POINT + 1):
                # допускаем небольшие отклонения вокруг целевой точки
                delta_temp = uniform(-0.05, 0.05)
                measured_temp = temp + delta_temp
                thermal_delta_r = base_r0 * _ALPHA * delta_temp
                measured_res = nominal_res + thermal_delta_r + uniform(-0.002, 0.002)
                error = measured_res - nominal_res

                measured_temp_raw.append(measured_temp)
                measured_res_raw.append(measured_res)

                measurements.append(
                    {
                        "idx": str(meas_idx),
                        "measured_temp": _fmt(measured_temp, 3),
                        "measured_signal": _fmt(measured_res, 3),
                        "error": _fmt(error, 3),
                    }
                )

                flat_rows.append(
                    {
                        "idx": str(meas_idx),
                        "set_temp": _fmt(temp if meas_idx == 1 else "", 0),
                        "calc_signal": _fmt(nominal_res if meas_idx == 1 else "", 2),
                        "measured_temp": _fmt(measured_temp, 3),
                        "measured_signal": _fmt(measured_res, 3),
                        "error": _fmt(error, 3),
                        "allowable": _fmt(float(allowable), 3) if meas_idx == 1 else "",
                    }
                )

            avg_temp = mean(measured_temp_raw) if measured_temp_raw else 0.0
            avg_res = mean(measured_res_raw) if measured_res_raw else 0.0
            avg_error = avg_res - nominal_res

            groups.append(
                {
                    "set_temp": _fmt(temp, 0),
                    "calc_signal": _fmt(nominal_res, 2),
                    "allowable": _fmt(float(allowable), 3),
                    "measurements": measurements,
                    "average": {
                        "measured_temp": _fmt(avg_temp, 3),
                        "measured_signal": _fmt(avg_res, 3),
                        "error": _fmt(avg_error, 3),
                    },
                    "average_raw": {"temperature": avg_temp, "resistance": avg_res},
                }
            )

            flat_rows.append(
                {
                    "idx": "ср. знач.",
                    "set_temp": "",
                    "calc_signal": "",
                    "measured_temp": _fmt(avg_temp, 3),
                    "measured_signal": _fmt(avg_res, 3),
                    "error": _fmt(avg_error, 3),
                    "allowable": "",
                }
            )

        r0_nominal = _TARGET_POINTS[0][1]
        r0_measured_val = groups[0]["average_raw"]["resistance"] if groups else 0.0
        r100_measured_val = groups[1]["average_raw"]["resistance"] if len(groups) > 1 else 0.0

        r0_deviation_pct = (
            ((r0_measured_val - r0_nominal) / r0_nominal) * 100.0 if r0_nominal else 0.0
        )
        w100_value = r100_measured_val / r0_measured_val if r0_measured_val else 0.0

        return {
            "rows": flat_rows,
            "point_groups": groups,
            "unit_label": "Ом",
            "allowable_error": _fmt(max(_ALLOWABLE_BY_POINT.values()), 3),
            "r0_deviation_pct": _fmt(r0_deviation_pct, 3),
            "r0_allowable_pct": _fmt(
                gi.allowable_variation.value(ref=r0_nominal, fsv=gi.range_max, ctx=gi.ctx), 3
            ),
            "w100_value": _fmt(w100_value, 4),
            "w100_allowable": "1.3850",
        }


GENERATOR = RTDGenerator()
TEMPLATE_ID = "rtd_platinum"
