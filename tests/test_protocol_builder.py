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
