from __future__ import annotations

from random import uniform

from .base import GenInput, TableGenerator

SET_VALUES_MA: tuple[float, ...] = (4.0, 8.0, 12.0, 16.0, 20.0)
SPAN_MA: float = max(SET_VALUES_MA) - min(SET_VALUES_MA)
DELTA_LIMIT_MA: float = 0.015  # keep error within ±0.1 % относительно диапазона 16 мА


def _fmt(value: float, digits: int) -> str:
    return f"{value:.{digits}f}"


class Controller43790(TableGenerator):
    """Генератор таблицы результатов для контроллеров 43790-12."""

    def generate(self, gi: GenInput) -> dict[str, object]:
        rows: list[dict[str, str]] = []

        for idx, set_ma in enumerate(SET_VALUES_MA):
            delta = uniform(-DELTA_LIMIT_MA, DELTA_LIMIT_MA)
            measured = set_ma + delta
            error_pct = ((measured - set_ma) / SPAN_MA) * 100.0

            rows.append(
                {
                    "channel": "1" if idx == 0 else "",
                    "set_value": _fmt(set_ma, 3),
                    "measured_value": _fmt(measured, 3),
                    "error_pct": _fmt(error_pct, 3),
                }
            )

        allowable_pct = gi.allowable_error.value(ref=gi.range_max, fsv=gi.range_max, ctx=gi.ctx)

        return {
            "rows": rows,
            "unit_label": "мА",
            "allowable_error": f"{allowable_pct:.2f}",
            "allowable_note": (
                "- ± 0,1 % (0,02 мА) - пределы допускаемой приведенной погрешности в "
                "рабочих условиях"
            ),
        }


GENERATOR = Controller43790()
TEMPLATE_ID = "controller_43790_12"
