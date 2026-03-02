# Hurl smoke-test для строки:
# Наименование: Измеритель влажности и температуры
# Модификация: ИВТМ-7
# Заводской номер: 96320
# № Свид-ва о поверке: С-ВСА/02-06-2025/436974158
#
# Запуск:
#   hurl --variable base_url=http://127.0.0.1:8000 tests/hurl/resolve_vri_id_ivt7.hurl

GET https://fgis.gost.ru/fundmetrology/eapi/vri?year=2021
HTTP 200
[Asserts]
jsonpath "$.vri_id" exists
