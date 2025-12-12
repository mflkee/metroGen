from __future__ import annotations

# базовые шаблоны
TEMPLATES: dict[str, dict] = {
    "pressure_common": {
        "title": "Манометры / датчики давления — общий",
        "points": 8,
        "allowable_variation_pct": 1.5,
        "path": "pressure.html",
        "fields": [
            "device_info",
            "mitypeNumber",
            "manufactureNum",
            "manufactureYear",
            "owner_name",
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
            "trainee_name",
            "trainee_note",
            "trainee_sign_src",
            "trainee_sign_style",
        ],
    },
    "controller_43790_12": {
        "title": "Контроллеры 43790-12",
        "points": 5,
        "allowable_variation_pct": 0.1,
        "path": "controller_43790_12.html",
        "fields": [
            "device_info",
            "mitypeNumber",
            "manufactureNum",
            "manufactureYear",
            "owner_name",
            "methodology_full",
            "methodology_points",
            "temperature",
            "humidity",
            "pressure",
            "etalon_line_top",
            "etalon_line_bottom",
            "table_rows",
            "allowable_note",
            "verification_date",
            "verifier_name",
        ],
    },
    "rtd_platinum": {
        "title": "Термопреобразователи сопротивления",
        "points": 2,
        "allowable_variation_pct": 0.05,
        "path": "rtd.html",
        "fields": [
            "device_info",
            "mitypeNumber",
            "manufactureNum",
            "manufactureYear",
            "owner_name",
            "methodology_full",
            "methodology_points",
            "temperature",
            "humidity",
            "pressure",
            "etalon_line_top",
            "etalon_line_bottom",
            "table_rows",
            "point_groups",
            "allowable_error",
            "verification_date",
            "verifier_name",
            "r0_deviation_pct",
            "r0_allowable_pct",
            "w100_value",
            "w100_allowable",
        ],
    },
    # добавляй новые шаблоны ниже
    # "thermometer_mercury": {...},
    # "rtp_tsp": {...},
}


def resolve_template_id(method_code: str, mitype_number: str, mitype_title: str) -> str:
    mt = (mitype_title or "").upper()
    mn = (mitype_number or "").upper()
    mc = (method_code or "").upper()

    # простые эвристики выбора
    if "8.461" in mc or "8.461" in mt or "8.461" in mn or "ТЕРМОПРЕОБРАЗОВ" in mt:
        return "rtd_platinum"
    if mn == "43790-12" or "СГМ ЭРИС-100" in mt:
        return "controller_43790_12"
    if "МАНОМЕТР" in mt or mn == "13535-93":
        return "pressure_common"

    # по умолчанию
    return "pressure_common"
