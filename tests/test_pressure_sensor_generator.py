from app.services.generators.base import FixedPctTol, GenInput
from app.services.generators.pressure_sensor import GENERATOR
from app.services.templates import resolve_template_id


def _gi(points: int = 5, allowable: float = 0.075) -> GenInput:
    return GenInput(
        range_min=0.0,
        range_max=18.0,
        unit="МПа",
        points=points,
        allowable_error=FixedPctTol(allowable),
        allowable_variation=FixedPctTol(allowable),
        ctx={},
    )


def test_pressure_sensor_rows_and_signal_range():
    for _ in range(50):
        result = GENERATOR.generate(_gi())
        rows = result["rows"]
        assert len(rows) == 5

        assert rows[0]["pressure"] == "0"
        assert rows[0]["nominal_ma"] == "4.000"
        assert rows[-1]["nominal_ma"] == "20.000"

        for row in rows:
            meas_fwd = float(row["meas_fwd"])
            meas_rev = float(row["meas_rev"])
            # сигнал остаётся в пределах 4..20 мА (с малым допуском)
            assert 3.99 <= meas_fwd <= 20.01
            assert 3.99 <= meas_rev <= 20.01


def test_pressure_sensor_errors_within_allowable():
    allowable = 0.075
    for _ in range(200):
        result = GENERATOR.generate(_gi(allowable=allowable))
        for row in result["rows"]:
            assert abs(float(row["err_fwd"])) <= allowable
            assert abs(float(row["err_rev"])) <= allowable
            assert abs(float(row["variation"])) <= allowable


def test_resolve_template_id_picks_sensor_for_pressure_transducers():
    assert (
        resolve_template_id("МП 4212-012-2013", "32854-13", "Датчики давления")
        == "pressure_sensor"
    )
    assert (
        resolve_template_id(
            "МП 4212-012-2013", "32854-13", "Преобразователи давления измерительные"
        )
        == "pressure_sensor"
    )
    # стрелочные — по-прежнему манометровая таблица
    assert (
        resolve_template_id("МИ 2124-90", "13535-93", "Манометры показывающие")
        == "pressure_common"
    )
    # не давление — не датчики давления
    assert resolve_template_id("", "27284-09", "Уровнемеры") == "level_meter"
