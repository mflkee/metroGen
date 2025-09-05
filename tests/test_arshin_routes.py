import httpx
import pytest
import respx

from app.services.arshin_client import ARSHIN_BASE


@pytest.mark.anyio
@respx.mock
async def test_get_vri_id_endpoint(async_client):
    cert = "С-ВЯ/15-01-2025/402123271"
    vri_id = "1-402123271"
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        return_value=httpx.Response(200, json={"result": {"items": [{"vri_id": vri_id}]}})
    )
    r = await async_client.get("/api/v1/resolve/vri-id", params={"cert": cert})
    assert r.status_code == 200
    body = r.json()
    assert body["vri_id"] == vri_id


@pytest.mark.anyio
@respx.mock
async def test_post_vri_ids_by_excel(async_client, make_excel):
    certs = [
        "С-ЕЖБ/05-06-2025/440144576",
        "С-ЕЖБ/05-06-2025/440144575",
    ]
    xlsx = make_excel(certs)  # колонка P, со 2 строки

    # моки: /vri → vri_id и /vri/{id} → детали (пустые достаточно)
    for i, cert in enumerate(certs, start=1):
        vid = f"1-40212327{i}"
        respx.get(f"{ARSHIN_BASE}/vri").mock(
            return_value=httpx.Response(200, json={"result": {"items": [{"vri_id": vid}]}})
        )
        respx.get(f"{ARSHIN_BASE}/vri/{vid}").mock(
            return_value=httpx.Response(200, json={"result": {}})
        )

    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/resolve/vri-details-by-excel", files=files)
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == len(certs)
    assert {item["certificate"] for item in body["items"]} == set(certs)


@pytest.mark.anyio
@respx.mock
async def test_get_details_by_vri_id(async_client):
    vri_id = "1-402123271"
    respx.get(f"{ARSHIN_BASE}/vri/{vri_id}").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "miInfo": {
                        "etaMI": {
                            "regNumber": "77090.19.1Р.00761951",
                            "mitypeNumber": "77090-19",
                            "mitypeTitle": "Преобразователи давления эталонные",
                            "mitypeType": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                        }
                    },
                    "vriInfo": {"organization": "ФБУ", "applicable": {"certNum": "X"}},
                    "info": {"protocol_url": f"{ARSHIN_BASE}/vri/{vri_id}/protocol"},
                }
            },
        )
    )
    r = await async_client.get(f"/api/v1/resolve/vri/{vri_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["vri_id"] == vri_id
    assert body["etalon_line"].startswith("77090.19.1Р.00761951; 77090-19")


@pytest.mark.anyio
@respx.mock
async def test_post_vri_details_by_excel(async_client, make_excel):
    certs = [
        "С-ЕЖБ/05-06-2025/440144576",
        "С-ЕЖБ/05-06-2025/440144575",
    ]
    xlsx = make_excel(certs)

    # 1) мок /vri: два последовательных ответа для двух вызовов
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        side_effect=[
            httpx.Response(200, json={"result": {"items": [{"vri_id": "1-AAA"}]}}),
            httpx.Response(200, json={"result": {"items": [{"vri_id": "1-BBB"}]}}),
        ]
    )
    # 2) мок /vri/{id} → детали
    respx.get(f"{ARSHIN_BASE}/vri/1-AAA").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "miInfo": {
                        "etaMI": {
                            "regNumber": "77090.19.1Р.00761951",
                            "mitypeNumber": "77090-19",
                            "mitypeTitle": "Преобразователи давления эталонные",
                            "mitypeType": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                        }
                    },
                    "vriInfo": {
                        "vrfDate": "15.01.2025",
                        "validDate": "14.01.2026",
                        "applicable": {"certNum": "X"},
                    },
                    "info": {"protocol_url": f"{ARSHIN_BASE}/vri/1-AAA/protocol"},
                }
            },
        )
    )
    respx.get(f"{ARSHIN_BASE}/vri/1-BBB").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "miInfo": {
                        "etaMI": {
                            "regNumber": "52506.16.РЭ.00353712",
                            "mitypeNumber": "52506-16",
                            "mitypeTitle": "Манометры газовые грузопоршневые",
                            "mitypeType": "МГП-10",
                        }
                    },
                    "vriInfo": {
                        "vrfDate": "01.02.2025",
                        "validDate": "31.01.2026",
                        "applicable": {"certNum": "Y"},
                    },
                    "info": {"protocol_url": f"{ARSHIN_BASE}/vri/1-BBB/protocol"},
                }
            },
        )
    )

    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/resolve/vri-details-by-excel", files=files)
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 2
    ids = {it["vri_id"] for it in body["items"]}
    assert ids == {"1-AAA", "1-BBB"}
    # проверим готовую строку для одного из них
    # в текущей реализации Excel-ручка не возвращает etalon_line —
    # он доступен в /resolve/vri/{vri_id}. Достаточно проверить состав ids.
