import io

import httpx
import pytest
import respx
from openpyxl import Workbook
from pathlib import Path

from app.services.arshin_client import ARSHIN_BASE
from app.utils.excel import CERTIFICATE_HEADER_KEYS


def _make_protocols_excel_row(
    certificate: str,
    sn: str = "ABC123",
    date: str = "15.01.2025",
    header: str = CERTIFICATE_HEADER_KEYS[-1],
) -> bytes:
    """Готовит XLSX с минимально нужной шапкой для /protocols/context-by-excel."""
    wb = Workbook()
    ws = wb.active
    ws["A1"] = header
    ws["B1"] = "Заводской номер"
    ws["C1"] = "Дата поверки"

    ws["A2"] = certificate
    ws["B2"] = sn
    ws["C2"] = date

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_manometers_excel_row(
    *,
    certificate: str,
    serial: str,
    verifier: str = "Большаков С.Н.",
    date: str = "15.06.2025",
    pressure: str = "101,5 кПа",
    owner: str = "ООО \"РИ-ИНВЕСТ\"",
) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "Обозначение СИ"
    ws["B1"] = "Заводской номер"
    ws["E1"] = "Владелец СИ"
    ws["F1"] = "Дата поверки"
    ws["H1"] = "Методика поверки"
    ws["J1"] = "Прочие сведения"
    ws["K1"] = "Поверитель"
    ws["M1"] = "Давление"
    ws["P1"] = "Свидетельство о поверке"

    ws["A2"] = "13535-93"
    ws["B2"] = serial
    ws["E2"] = owner
    ws["F2"] = date
    ws["H2"] = "МИ 2124-90"
    ws["J2"] = "(0 - 4) кгс/см²"
    ws["K2"] = verifier
    ws["M2"] = pressure
    ws["P2"] = certificate

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_manometers_db_excel(
    *,
    serial: str,
    certificate: str,
    protocol_number: str,
) -> bytes:
    wb = Workbook()
    ws = wb.active

    ws["H5"] = "Заводской №/ Буквенно-цифровое обозначение"
    ws["L5"] = "Документ"
    ws["P5"] = "номер_протокола"

    ws["H6"] = serial
    ws["L6"] = certificate
    ws["P6"] = protocol_number

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.anyio
@respx.mock
@pytest.mark.parametrize("header", CERTIFICATE_HEADER_KEYS)
async def test_contexts_by_excel_happy_path(async_client, header):
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

    xlsx = _make_protocols_excel_row(cert, header=header)
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


@pytest.mark.anyio
@respx.mock
async def test_manometers_pdf_files_happy_path(async_client, tmp_path, monkeypatch):
    cert = "С-ЕЖБ/05-06-2025/443771099"
    serial = "03607"
    protocol_num = "06/001/25"
    vri_id = "1-MANO"

    manometers_xlsx = _make_manometers_excel_row(certificate=cert, serial=serial)
    db_xlsx = _make_manometers_db_excel(serial=serial, certificate=cert, protocol_number=protocol_num)

    async def fake_pdf(html: str) -> bytes | None:
        assert "ПРОТОКОЛ" in html
        return b"%PDF-manometer%"

    monkeypatch.setattr("app.api.routes.protocols.html_to_pdf_bytes", fake_pdf)
    monkeypatch.setattr("app.api.routes.protocols.get_dated_exports_dir", lambda _day: tmp_path)

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
                        "vrfDate": "15.06.2025",
                        "validDate": "14.06.2026",
                        "applicable": {"certNum": cert},
                    },
                }
            },
        )
    )

    files = {
        "manometers_file": (
            "manometers.xlsx",
            manometers_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        "db_file": (
            "db.xlsx",
            db_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    }

    response = await async_client.post("/api/v1/protocols/manometers/pdf-files", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["errors"] == []
    assert len(body["files"]) == 1

    saved_path = Path(body["files"][0])
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"%PDF-manometer%"
    assert saved_path.parent == tmp_path
    assert saved_path.name == "06-001-25.pdf"


@pytest.mark.anyio
@respx.mock
async def test_manometers_pdf_files_certificate_mismatch(async_client, tmp_path, monkeypatch):
    serial = "03607"
    excel_cert = "С-ЕЖБ/05-06-2025/443771999"
    db_cert = "С-ЕЖБ/05-06-2025/443771099"
    protocol_num = "06/001/25"

    manometers_xlsx = _make_manometers_excel_row(certificate=excel_cert, serial=serial)
    db_xlsx = _make_manometers_db_excel(serial=serial, certificate=db_cert, protocol_number=protocol_num)

    calls = {"pdf": 0}

    async def fake_pdf(html: str) -> bytes | None:
        calls["pdf"] += 1
        return b"%PDF%"

    monkeypatch.setattr("app.api.routes.protocols.html_to_pdf_bytes", fake_pdf)
    monkeypatch.setattr("app.api.routes.protocols.get_dated_exports_dir", lambda _day: tmp_path)

    files = {
        "manometers_file": (
            "manometers.xlsx",
            manometers_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        "db_file": (
            "db.xlsx",
            db_xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
    }

    response = await async_client.post("/api/v1/protocols/manometers/pdf-files", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 0
    assert body["files"] == []
    assert len(body["errors"]) == 1
    error = body["errors"][0]
    assert error["reason"] == "certificate mismatch between excel and db"
    assert error["serial"] == serial
    assert calls["pdf"] == 0
