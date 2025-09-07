from __future__ import annotations

# базовые шаблоны
TEMPLATES: dict[str, dict] = {
    "pressure_common": {
        "title": "Манометры / датчики давления — общий",
        "points": 8,
        "allowable_variation_pct": 1.5,
        "path": "manometer.html",
        "fields": [
            "device_info",
            "mitypeNumber",
            "manufactureNum",
            "manufactureYear",
            "owner_name",
            "owner_inn",
            "methodology_full",
            "methodology_points",
            "temperature",
            "humidity",
            "pressure",
            "etalon_line_top",
            "etalon_line_bottom",
            "table_rows",
            "unit",
            "allowable_error_fmt",
            "allowable_variation",
            "verification_date",
            "verifier_name",
        ],
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
