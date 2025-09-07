import io

import httpx
import pytest
import respx
from openpyxl import Workbook

from app.services.arshin_client import ARSHIN_BASE


def _make_excel_row(certificate: str, sn: str = "ABC123", date: str = "15.01.2025") -> bytes:
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
async def test_html_by_excel_returns_html(async_client):
    cert = "С-ВЯ/15-01-2025/402123271"
    vri_id = "1-XYZ"

    # 1) /vri (по номеру свидетельства)
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

    # 2) /vri/{id}
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

    xlsx = _make_excel_row(cert)
    files = {
        "file": (
            "input.xlsx",
            xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    r = await async_client.post("/api/v1/protocols/html-by-excel", files=files)

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    html = r.text
    assert "ПРОТОКОЛ ПЕРИОДИЧЕСКОЙ ПОВЕРКИ" in html
    assert "ABC123" in html  # serial number appears
    assert "МИ 123-45" in html  # methodology
    assert "77090-19" in html  # etalon line

