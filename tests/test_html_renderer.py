import pytest

from app.services.html_renderer import render_protocol_html
from app.services.protocol_builder import build_context

_DEFAULT_POINTS = {"p1": "5.1", "p2": "5.2", "p3": "5.3"}


def test_pressure_template_keeps_its_own_table_without_a_structure():
    """Фоллбэк: без structure_table шаблон рисует свою прежнюю шапку."""
    html = render_protocol_html(
        {
            "template_id": "pressure_common",
            "unit": "кгс/см²",
            "allowable_error": "1.50",
            "allowable_variation": "1.50",
            "table_rows": [
                {
                    "si_fwd": "1.00",
                    "si_rev": "1.01",
                    "ref_fwd": "1.000",
                    "ref_rev": "1.000",
                    "err_fwd": "0.00",
                    "err_rev": "0.01",
                    "var_pct": "0.01",
                }
            ],
        }
    )

    assert "Приведенная погрешность" in html
    assert "Допустимая вариация" in html
    assert "1.00" in html


def test_pressure_template_renders_the_structure_table():
    """Когда builder положил structure_table, главная таблица собирается из структуры."""
    html = render_protocol_html(
        {
            "template_id": "pressure_common",
            "structure_table": {
                "columns": [
                    {"id": "si_fwd", "title": "Мои показания"},
                    {"id": "allowable_error", "title": "Допуск"},
                ],
                "rows": [["1.00", "1.50"], ["2.00", "1.50"]],
            },
        }
    )

    assert "Мои показания" in html
    assert "Допуск" in html
    assert "2.00" in html
    # Прежней шапки больше нет — таблицу задаёт структура.
    assert "Приведенная погрешность" not in html


@pytest.mark.anyio
async def test_pressure_html_renders_range_class_auxiliary_and_summary():
    excel_row = {
        "Обозначение СИ": "4041-93",
        "Заводской номер": "00435",
        "Модификация": "ДМ2005СгУ3",
        "Прочие сведения": "0…0,6 МПа",
        "КТ": "1,5",
        "Методика поверки": "МИ 2124-90",
        "Температура": "21,5",
        "Влажность": "60",
        "Давление": "102,3 кПа",
        "_resolved_auxiliary_instruments": [
            {
                "title": "Измерители влажности и температуры",
                "modification": "ИВТМ-7 М5-Д",
                "manufacture_num": "96320",
                "reg_number": "71394-18",
                "certificate_no": "С-ВСА/02-06-2025/436974158",
                "verification_date": "2025-06-02",
                "valid_to": "2026-06-01",
            }
        ],
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "4041-93"}},
        "vriInfo": {"vrfDate": "15.01.2025", "validDate": "14.01.2026"},
        "means": {
            "mieta": [
                {
                    "regNumber": "77090.19.2Р.01262797",
                    "mitypeNumber": "77090-19",
                    "mitypeTitle": "Преобразователи давления эталонные",
                    "notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                    "modification": "модификация 1М",
                    "manufactureNum": "4234",
                    "manufactureYear": 2025,
                    "rankCode": "2Р",
                    "rankTitle": "Эталон 2-го разряда",
                }
            ]
        },
    }

    ctx = await build_context(
        excel_row=excel_row,
        details=details,
        methodology_points=dict(_DEFAULT_POINTS),
        owner_name='ООО "РИ-ИНВЕСТ"',
        owner_inn="7705551779",
        allowable_error=1.5,
        allowable_variation=1.5,
        protocol_number="01/001/26",
    )

    html = render_protocol_html(ctx)

    assert "Диапазон измерений:" in html
    assert "0…0,6 МПа" in html
    assert "Класс точности:" in html
    assert "1,5" in html
    assert "Не эталоны:" not in html
    assert "71394-18; Измерители влажности и температуры; ИВТМ-7 М5-Д" in html
    assert 'Место проведения поверки:' in html
    assert 'ООО "МКАИР"' in html
    assert "Вибрация (тряска) отсутствует (не вызывает колебаний стрелки)" in html
    assert ">60%<" in html or "> 60%<" in html
    assert "Максимальное полученное значение вариации:" in html
    assert f'{ctx["max_variation_value"]} {ctx["max_variation_unit"]}' in html
    assert "Максимальное полученное значение абсолютной погрешности:" not in html
    assert "°С," in html
    assert '<p class="line">атмосферное давление ' in html

    temp_idx = html.index("температура окружающего воздуха")
    humidity_idx = html.index("относительная влажность")
    pressure_idx = html.index("атмосферное давление")
    vibration_idx = html.index("Вибрация (тряска) отсутствует (не вызывает колебаний стрелки)")
    undertext_idx = html.index(
        "Указываются влияющие факторы, нормированные в НД на методику поверки,"
    )
    assert temp_idx < humidity_idx < pressure_idx < vibration_idx < undertext_idx


@pytest.mark.anyio
async def test_pressure_html_normalizes_fractional_humidity_to_percent():
    excel_row = {
        "Обозначение СИ": "4041-93",
        "Заводской номер": "00435",
        "Модификация": "ДМ2005СгУ3",
        "Прочие сведения": "0…0,6 МПа",
        "КТ": "1,5",
        "Методика поверки": "МИ 2124-90",
        "Влажность": 0.34,
    }
    details = {
        "miInfo": {"singleMI": {"mitypeTitle": "Манометры", "mitypeNumber": "4041-93"}},
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

    html = render_protocol_html(ctx)

    assert ">34%<" in html or "> 34%<" in html
