import pytest

from app.services.generators.base import FixedPctTol, GenInput
from app.services.generators.pressure_common import GENERATOR


@pytest.mark.parametrize("allowable_variation", [0.1, 0.5, 1.0, 1.5])
def test_pressure_generator_keeps_variation_below_allowable_with_margin(allowable_variation):
    gi = GenInput(
        range_min=0.0,
        range_max=4.0,
        unit="кгс/см²",
        points=8,
        allowable_error=FixedPctTol(1.5),
        allowable_variation=FixedPctTol(allowable_variation),
        ctx={},
    )

    # Проверяем многократно, чтобы исключить случайные выбросы.
    for _ in range(120):
        result = GENERATOR.generate(gi)
        rows = result["rows"]
        assert rows
        for row in rows:
            var_pct = float(row["var_pct"])
            assert var_pct <= (allowable_variation - 0.01)
