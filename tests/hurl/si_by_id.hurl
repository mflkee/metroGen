# Fetch details by known vri_id
GET {{base_url}}/vri/{{vri_id}}
HTTP 200
[Asserts]
jsonpath "$.result" exists
jsonpath "$.result.vriInfo" exists
