import pytest

from app.api.routes import protocols
from app.services import html_renderer


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("09 БД.xlsx", "09"),
        ("registry_2025-08.xlsx", "08"),
        ("export_202507_data.xlsx", "07"),
        ("no_month.xlsx", None),
    ],
)
def test_extract_month_from_filename(filename, expected):
    assert protocols._extract_month_from_filename(filename) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("24,2 °С°С", "24,2"),
        (" 19.50 ", "19,5"),
        ("темп 12.0 C", "12"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_temperature_plain(value, expected):
    assert html_renderer._normalize_temperature_plain(value) == expected
