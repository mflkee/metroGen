from __future__ import annotations

# базовые шаблоны
TEMPLATES: dict[str, dict] = {
    "pressure_common": {
        "title": "Манометры / датчики давления — общий",
        "points": 8,
        "allowable_variation_pct": 1.5,
    },
    # добавляй новые шаблоны ниже
    # "thermometer_mercury": {...},
    # "rtp_tsp": {...},
}


def resolve_template_id(method_code: str, mitype_number: str, mitype_title: str) -> str:
    mt = (mitype_title or "").upper()
    mn = (mitype_number or "").upper()

    # простые эвристики выбора
    if "МАНОМЕТР" in mt or mn == "13535-93":
        return "pressure_common"

    # по умолчанию
    return "pressure_common"
