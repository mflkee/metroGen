import io

import httpx
import pytest
import respx
from openpyxl import Workbook

from app.services.arshin_client import ARSHIN_BASE


def _make_protocols_excel_row(
    certificate: str,
    sn: str = "ABC123",
    date: str = "15.01.2025",
) -> bytes:
    """Готовит XLSX с минимально нужной шапкой для /protocols/context-by-excel."""
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "Номер свидетельтсва"
    ws["B1"] = "Заводской номер"
    ws["C1"] = "Дата поверки"

    ws["A2"] = certificate
    ws["B2"] = sn
    ws["C2"] = date

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.anyio
@respx.mock
async def test_contexts_by_excel_happy_path(async_client):
    cert = "С-ВЯ/15-01-2025/402123271"
    vri_id = "1-XYZ"

    # 1) /vri (по номеру свидетельства) → vri_id
    # 2) /vri (по данным эталона)      → свидетельство эталона (второй вызов того же URL)
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        side_effect=[
            httpx.Response(200, json={"result": {"items": [{"vri_id": vri_id}]}}),
            httpx.Response(
                200,
                json={
                    "result": {
                        "items": [
                            {
                                "result_docnum": "ET-123",
                                "verification_date": "01.01.2025",
                                "valid_date": "31.12.2025",
                            }
                        ]
                    }
                },
            ),
        ]
    )

    # 3) /vri/{id} → детали для билдера
    respx.get(f"{ARSHIN_BASE}/vri/{vri_id}").mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "means": {
                        "mieta": [
                            {
                                "regNumber": "77090.19.1Р.00761951",
                                "mitypeNumber": "77090-19",
                                "mitypeTitle": "Преобразователи давления эталонные",
                                "notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                                "manufactureNum": "3127",
                                "manufactureYear": 2020,
                                "rankCode": "1Р",
                                "rankTitle": "Эталон 1-го разряда",
                            }
                        ]
                    },
                    "vriInfo": {
                        "docTitle": "МИ 123-45",
                        "vrfDate": "15.01.2025",
                        "validDate": "14.01.2026",
                        "applicable": {"certNum": cert},
                    },
                }
            },
        )
    )

    xlsx = _make_protocols_excel_row(cert)
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/context-by-excel", files=files)

    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    item = body["items"][0]

    # Проверяем основные поля
    assert item["certificate"] == cert
    assert item["vri_id"] == vri_id
    assert item["filename"] == "ABC123-б-150125-1"
    # В контексте должна появиться строка эталона
    assert "77090-19" in (item["context"] or {}).get("etalon_line", "")


@pytest.mark.anyio
@respx.mock
async def test_contexts_by_excel_empty_certificate(async_client):
    # Пустой номер → элемент с ошибкой
    xlsx = _make_protocols_excel_row("")
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/context-by-excel", files=files)

    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["error"] == "certificate number is empty"
    assert item["vri_id"] == ""


@pytest.mark.anyio
@respx.mock
async def test_contexts_by_excel_not_found(async_client):
    cert = "С-ВЯ/15-01-2025/000000001"
    # /vri не находит запись
    respx.get(f"{ARSHIN_BASE}/vri").mock(
        return_value=httpx.Response(200, json={"result": {"items": []}})
    )

    xlsx = _make_protocols_excel_row(cert)
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/context-by-excel", files=files)

    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["certificate"] == cert
    assert item["error"] == "not found"
    assert item["vri_id"] == ""
