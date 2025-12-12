import random

import pytest

from app.services.protocol_builder import build_context

_DEFAULT_POINTS = {"p1": "5.1", "p2": "5.2", "p3": "5.3"}


def test_owner_name_fallback_uses_alternative_headers():
    from app.services import protocol_builder as pb

    row = {
        "Организация": 'ООО "РИ-ИНВЕСТ"',
        "Владелец": "",
        "Владелец СИ": "",
    }
    assert pb._owner_name_from_row(row) == 'ООО "РИ-ИНВЕСТ"'


def test_raw_allowable_value_supports_multiple_headers():
    from app.services import protocol_builder as pb

    row = {"Другие параметры": "0,8", "КТ": "1,0"}
    assert pb._raw_allowable_value(row) == "0,8"

    row = {"КТ": "1,2"}
    assert pb._raw_allowable_value(row) == "1,2"

    row = {"кт": "0,075"}
    assert pb._raw_allowable_value(row) == "0,075"

    row = {"Другие параметры": "", "КТ": None}
    assert pb._raw_allowable_value(row) is None


def test_parse_allowable_value_handles_percent_and_comma():
    from app.services import protocol_builder as pb

    assert pb._parse_allowable_value("0,075 %", 1.5) == pytest.approx(0.075)
    assert pb._parse_allowable_value("1.2%", 1.5) == pytest.approx(1.2)
    assert pb._parse_allowable_value(None, 1.5) == pytest.approx(1.5)


def test_display_allowable_value_prefers_raw_text():
    from app.services import protocol_builder as pb

    assert pb._display_allowable_value("0,075 %", 0.075) == "0,075"
    assert pb._display_allowable_value("0.018%", 0.018) == "0.018"
    assert pb._display_allowable_value(None, 0.05) == "0.05"


@pytest.mark.anyio
async def test_build_context_rtd_template_extra_fields():
    excel_row = {
        "Обозначение СИ": "71040-18",
        "Заводской номер": "11856/19/1/06",
        "Методика поверки": "ГОСТ 8.461-2009",
        "Прочие сведения": "(-196…600) °С",
    }
    details = {
        "miInfo": {
            "singleMI": {
                "mitypeTitle": "Термопреобразователи сопротивления",
                "mitypeNumber": "71040-18",
            }
        },
        "vriInfo": {},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="7705550000",
        allowable_error=0.05,
        allowable_variation=0.05,
    )

    assert ctx["template_id"] == "rtd_platinum"
    assert ctx.get("r0_deviation_pct") is not None
    assert ctx.get("w100_value") is not None


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
        "miInfo": {
            "singleMI": {"mitypeTitle": "Манометры показывающие", "mitypeNumber": "13535-93"}
        },
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
async def test_build_context_raises_when_owner_inn_missing():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
    }
    details = {"miInfo": {"singleMI": {}}, "vriInfo": {}}

    with pytest.raises(ValueError, match="owner INN not found"):
        await build_context(
            excel_row=excel_row,
            details=details,
            methodology_points=dict(_DEFAULT_POINTS),
            owner_name="ООО Тест",
            owner_inn="",
            allowable_error=1.5,
            allowable_variation=1.5,
        )


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
        owner_inn="7705550000",
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
        "miInfo": {
            "singleMI": {"mitypeTitle": "Манометры показывающие", "mitypeNumber": "13535-93"}
        },
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
        owner_inn="7705550000",
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
        owner_inn="7705550000",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    assert ctx["range_min"] == -300
    assert ctx["range_max"] == 300
    assert ctx["unit"] == "mbar"
    assert ctx["range_source"] == "excel"
    assert ctx["table_rows"], "generator should build rows when range parsed"


@pytest.mark.anyio
async def test_build_context_uses_allowable_variation_from_excel():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Прочие сведения": "(0 ... 21) МПа",
        "Методика поверки": "МИ 2124-90",
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "13535-93"}},
        "vriInfo": {},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="7705550000",
        allowable_error=0.075,
        allowable_variation=0.075,
    )

    assert ctx["allowable_variation"] == ctx["allowable_error_fmt"]


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
        owner_inn="7705550000",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    entries = ctx["etalon_entries"]
    assert len(entries) == 2
    assert entries[0]["reg_number"] == "REG-1"
    assert entries[1]["reg_number"] == "REG-2"
    assert entries[1]["certificate_line"].startswith("свидетельство о поверке № ET-2")
    assert ctx["etalon_lines"][0].startswith("REG-1; TYPE-1")


@pytest.mark.anyio
async def test_build_context_uses_arshin_range_when_excel_missing():
    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Методика поверки": "МИ 2124-90",
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "13535-93"}},
        "info": {"additional_info": "0 .. 10 кг/см²"},
        "vriInfo": {},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="7705550000",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    assert ctx["range_min"] == 0
    assert ctx["range_max"] == 10
    assert ctx["unit"] == "кгс/см²"
    assert ctx["range_source"] == "arshin"


@pytest.mark.anyio
async def test_build_context_selects_controller_template():
    excel_row = {
        "Обозначение СИ": "43790-12",
        "Заводской номер": "CTRL-01",
        "Методика поверки": "МИ 5555-55",
        "Прочие сведения": "4 .. 20 мА",
    }
    details = {
        "miInfo": {
            "singleMI": {
                "mitypeTitle": "Контроллер 43790-12",
                "mitypeNumber": "43790-12",
            }
        },
        "vriInfo": {"vrfDate": "01.03.2025", "validDate": "01.03.2026"},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО Контур",
        owner_inn="7701234567",
        allowable_error=0.1,
        allowable_variation=0.1,
    )

    assert ctx["template_id"] == "controller_43790_12"
    assert ctx["allowable_note"].startswith("- ± 0,1 %")
    assert ctx["table_rows"], "controller generator should build table rows"


@pytest.mark.anyio
async def test_build_context_adds_trainee_signature_for_2023(monkeypatch):
    from app.services import protocol_builder as pb

    dummy_signature = type("Sig", (), {"src": "sig-data", "style": "sig-style"})()
    monkeypatch.setattr(pb, "_NAME_RNG", random.Random(0))
    monkeypatch.setattr(pb, "get_signature_render", lambda name: dummy_signature)

    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Методика поверки": "МИ 2124-90",
        "Дата поверки": "15.06.2023",
        "Поверитель": "Чупин А.А.",
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "13535-93"}},
        "vriInfo": {},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="7705550000",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    assert ctx["trainee_name"] in {"Большаков С.Н.", "Запевахин Т.Е."}
    assert ctx["trainee_note"].startswith("(приказ о стажировке № 03-23-МС")
    assert ctx["trainee_sign_src"] == dummy_signature.src
    assert ctx["trainee_sign_style"] == dummy_signature.style


@pytest.mark.anyio
async def test_build_context_omits_trainee_for_other_years(monkeypatch):
    from app.services import protocol_builder as pb

    dummy_signature = type("Sig", (), {"src": "sig-data", "style": "sig-style"})()
    monkeypatch.setattr(pb, "_NAME_RNG", random.Random(0))
    monkeypatch.setattr(pb, "get_signature_render", lambda name: dummy_signature)

    excel_row = {
        "Обозначение СИ": "13535-93",
        "Заводской номер": "03607",
        "Методика поверки": "МИ 2124-90",
        "Дата поверки": "15.06.2024",
        "Поверитель": "Чупин А.А.",
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "13535-93"}},
        "vriInfo": {},
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name="ООО НПП",
        owner_inn="7705550000",
        allowable_error=1.5,
        allowable_variation=1.5,
    )

    assert ctx["trainee_name"] == ""
    assert ctx["trainee_note"] == ""
    assert ctx["trainee_sign_style"] == "display: none;"
