import pytest

from app.services.protocol_builder import build_context


_DEFAULT_POINTS = {"p1": "5.1", "p2": "5.2", "p3": "5.3"}


@pytest.mark.anyio
async def test_build_context_merges_type_and_modification_in_device_info():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Модификация": "ТМ3",
        "Прочие сведения": "(0 - 4) кгс/см²",
        "Дата поверки": "15.06.2025",
        "Методика поверки": "МИ 2124-90",
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры показывающие", "mitypeNumber": "13535-93"}},
        "vriInfo": {},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name='ООО "РИ-ИНВЕСТ"',
        owner_inn="7705551779",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    assert ctx["device_info"] == "Манометры показывающие, ТМ3"
    assert ctx["device_type_name"] == "Манометры показывающие"
    assert ctx["device_modification"] == "ТМ3"


@pytest.mark.anyio
async def test_build_context_falls_back_to_arshin_modification():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Прочие сведения": "(0 - 4) кгс/см²",
        "Методика поверки": "МИ 2124-90",
    }
    details = {
        "miInfo": {
            "singleMI": {
                "mitypeTitle": "Манометры показывающие",
                "mitypeNumber": "13535-93",
                "modification": "ДМ2010СгУ2",
            }
        },
        "vriInfo": {},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    assert ctx["device_info"] == "Манометры показывающие, ДМ2010СгУ2"
    assert ctx["device_modification"] == "ДМ2010СгУ2"


@pytest.mark.anyio
async def test_build_context_restores_default_point_descriptions_when_missing():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Методика поверки": "МИ 2124-90",
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры показывающие", "mitypeNumber": "13535-93"}},
        "vriInfo": {},
    }
    items = [
        {"position": 1, "code": "5.1", "point_type": "bool"},
        {"position": 2, "code": "5.2.3", "point_type": "bool"},
        {"position": 3, "code": "5.3", "point_type": "clause"},
        {"position": 4, "code": "5.4", "point_type": "bool"},
    ]

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        methodology_point_items=items,
        owner_name="ООО НПП",
        owner_inn="",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    descriptions = [item["description"] for item in ctx["methodology_point_items"]]
    assert descriptions[:3] == [
        "Результат внешнего осмотра",
        "Результат опробования",
        "Определение основной погрешности",
    ]
    assert descriptions[3] == ""
    assert len(ctx["methodology_point_items"]) == 4


@pytest.mark.anyio
async def test_build_context_parses_signed_ranges():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Прочие сведения": "(-300 - +300) mbar",
        "Дата поверки": "01.02.2025",
        "Методика поверки": "МИ 2124-90",
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "13535-93"}},
        "vriInfo": {"vrfDate": "01.02.2025", "validDate": "01.02.2026"},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    assert ctx["range_min"] == -300
    assert ctx["range_max"] == 300
    assert ctx["unit"] == "mbar"
    assert ctx["range_source"] == "excel"
    assert ctx["table_rows"], "generator should build rows when range parsed"


@pytest.mark.anyio
async def test_build_context_includes_all_etalons_from_details():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Методика поверки": "МИ 2124-90",
        "_resolved_etalon_certs": [
            {
                "line": "свидетельство о поверке № ET-1; действительно до 31.12.2024;",
                "manufacture_num": "E-001",
                "reg_number": "REG-1",
            },
            {
                "line": "свидетельство о поверке № ET-2; действительно до 31.12.2025;",
                "manufacture_num": "E-002",
                "reg_number": "REG-2",
            },
        ],
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "13535-93"}},
        "vriInfo": {},
        "means": {
            "mieta": [
                {
                    "regNumber": "REG-1",
                    "mitypeNumber": "TYPE-1",
                    "mitypeTitle": "Эталон 1",
                    "notation": "Нотация 1",
                    "manufactureNum": "E-001",
                },
                {
                    "regNumber": "REG-2",
                    "mitypeNumber": "TYPE-2",
                    "mitypeTitle": "Эталон 2",
                    "notation": "Нотация 2",
                    "manufactureNum": "E-002",
                },
            ]
        },
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    entries = ctx["etalon_entries"]
    assert len(entries) == 2
    assert entries[0]["reg_number"] == "REG-1"
    assert entries[1]["reg_number"] == "REG-2"
    assert entries[1]["certificate_line"].startswith("свидетельство о поверке № ET-2")
    assert ctx["etalon_lines"][0].startswith("REG-1; TYPE-1")
