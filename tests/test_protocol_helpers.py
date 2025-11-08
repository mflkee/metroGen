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


@pytest.mark.parametrize(
    ("ctx", "forced_month", "use_default_only", "expected"),
    [
        (
            {"equipment_label": "Манометры ПВ", "verification_date": "2025-06-15"},
            None,
            False,
            "PDF Манометры ПВ 06",
        ),
        (
            {"device_info": "Манометры TM", "verification_date": "2025-02-01"},
            "03",
            False,
            "PDF Манометры TM 03",
        ),
        (
            {"equipment_label": "Манометры TM", "verification_date": "2025-02-01"},
            None,
            True,
            "PDF Манометры 02",
        ),
    ],
)
def test_exports_folder_label(ctx, forced_month, use_default_only, expected):
    result = protocols._exports_folder_label(
        ctx,
        default_equipment="Манометры",
        forced_month=forced_month,
        use_default_only=use_default_only,
    )
    assert result == expected


@pytest.mark.parametrize(
    ("ctx", "expected"),
    [
        (
            {"verification_date": "2025-06-15", "Заводской номер": "04200", "mpi_years": 2},
            "2025-06-15 № 04200 (МПИ-2).pdf",
        ),
        ({}, "unknown-date.pdf"),
    ],
)
def test_context_pdf_filename(ctx, expected):
    assert protocols._context_pdf_filename(ctx) == expected
