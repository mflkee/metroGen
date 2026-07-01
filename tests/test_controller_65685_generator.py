from app.services.generators.base import FixedPctTol, GenInput
from app.services.generators.controller_65685_16 import CHANNEL_COUNT, GENERATOR, SET_VALUES_MA


def test_controller_65685_generator_produces_expected_rows(monkeypatch):
    monkeypatch.setattr(
        "app.services.generators.controller_65685_16.uniform",
        lambda *_args, **_kwargs: 0.0,
    )

    gi = GenInput(
        range_min=0.0,
        range_max=20.0,
        unit="мА",
        points=len(SET_VALUES_MA),
        allowable_error=FixedPctTol(0.1),
        allowable_variation=FixedPctTol(0.2),
        ctx={},
    )

    result = GENERATOR.generate(gi)

    assert result["unit_label"] == "мА"
    assert result["allowable_error"] == "0.10"
    assert result["allowable_note"].startswith("- ± 0,1 %")
    rows = result["rows"]
    expected_rows = CHANNEL_COUNT * len(SET_VALUES_MA)
    assert len(rows) == expected_rows
    # Channel numbers appear at the start of each channel block
    channel_starts = [row for row in rows if row["channel"]]
    assert len(channel_starts) == CHANNEL_COUNT
    assert channel_starts[0]["channel"] == "1"
    assert channel_starts[-1]["channel"] == str(CHANNEL_COUNT)
    assert all(row["error_pct"] == "0.000" for row in rows)
    assert rows[0]["set_value"] == f"{SET_VALUES_MA[0]:.3f}"
    assert rows[-1]["measured_value"] == f"{SET_VALUES_MA[-1]:.3f}"


def test_controller_65685_template_id():
    from app.services.generators.controller_65685_16 import TEMPLATE_ID

    assert TEMPLATE_ID == "controller_65685_16"
