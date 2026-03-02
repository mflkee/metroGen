# Hurl-сценарии по документации ФГИС «Аршин» для списка результатов поверки (eapi/vri)
#
# Что проверяем:
# 1) Список поверок за текущий год: /vri
# 2) Список поверок за указанный год: /vri?year=2021
# 3) Список поверок за конкретную дату: /vri?verification_date=2021-09-01
#
# Запуск:
#   hurl --variable base_url=https://fgis.gost.ru/fundmetrology/eapi tests/hurl/vri_list_docs_examples.hurl
#
# Примечание: сервис может возвращать 429 при частых запросах (>2 req/sec).

# 1) Текущий год (параметр year не передаём)
GET {{base_url}}/vri
HTTP 200
[Asserts]
jsonpath "$.result" exists
jsonpath "$.result.count" exists
jsonpath "$.result.start" exists
jsonpath "$.result.rows" exists
jsonpath "$.result.items" exists

# 2) Конкретный год
GET {{base_url}}/vri?year=2021
HTTP 200
[Asserts]
jsonpath "$.result" exists
jsonpath "$.result.count" exists
jsonpath "$.result.start" exists
jsonpath "$.result.rows" exists
jsonpath "$.result.items" exists

# 3) Конкретная дата поверки
GET {{base_url}}/vri?verification_date=2021-09-01
HTTP 200
[Asserts]
jsonpath "$.result" exists
jsonpath "$.result.count" exists
jsonpath "$.result.start" exists
jsonpath "$.result.rows" exists
jsonpath "$.result.items" exists
