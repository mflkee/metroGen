# 1) Search SI by year + mit_number + mi_number
GET {{base_url}}/vri
[QueryStringParams]
year: {{year}}
mit_number: {{mit_number}}
mi_number: {{mi_number}}
start: {{start}}
rows: {{rows}}
HTTP 200
[Asserts]
jsonpath "$.result.items" exists
jsonpath "$.result.items[0].vri_id" exists
[Captures]
found_vri_id: jsonpath "$.result.items[0].vri_id"

# 2) Fetch details by found vri_id
GET {{base_url}}/vri/{{found_vri_id}}
HTTP 200
[Asserts]
jsonpath "$.result" exists
jsonpath "$.result.vriInfo" exists
