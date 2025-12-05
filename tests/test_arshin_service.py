import httpx
import respx

from app.services.arshin_client import (
    ARSHIN_BASE,
    compose_etalon_line_from_details,
    extract_detail_fields,
    fetch_vri_details,
    fetch_vri_id_by_certificate,
)

CERT = "С-ВЯ/15-01-2025/402123271"
VRI_ID = "1-402123271"

LIST_PAYLOAD = {
    "result": {
        "count": 1,
        "start": 0,
        "rows": 10,
        "items": [
            {
                "vri_id": VRI_ID,
                "org_title": 'ФБУ "ТЮМЕНСКИЙ ЦСМ"',
                "mit_number": "77090-19",
                "mit_title": "Преобразователи давления эталонные",
                "mit_notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                "mi_modification": "1М-0,01-Т35",
                "mi_number": "3127",
                "verification_date": "15.01.2025",
                "valid_date": "14.01.2026",
                "result_docnum": CERT,
                "applicability": True,
            }
        ],
    }
}

DETAILS_PAYLOAD = {
    "result": {
        "miInfo": {
            "etaMI": {
                "regNumber": "77090.19.1Р.00761951",
                "mitypeNumber": "77090-19",
                "mitypeTitle": "Преобразователи давления эталонные",
                "mitypeType": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
                "manufactureNum": "3127",
                "manufactureYear": 2020,
                "rankCode": "1Р",
                "rankTitle": "Эталон 1-го разряда",
            }
        },
        "vriInfo": {
            "organization": 'ФБУ "ТЮМЕНСКИЙ ЦСМ"',
            "vrfDate": "15.01.2025",
            "validDate": "14.01.2026",
            "applicable": {"certNum": CERT},
        },
        "info": {"protocol_url": f"{ARSHIN_BASE}/vri/{VRI_ID}/protocol"},
    }
}


@respx.mock
async def test_fetch_vri_and_details():
    async with httpx.AsyncClient() as client:
        # мок: список по сертификату
        respx.get(f"{ARSHIN_BASE}/vri").mock(return_value=httpx.Response(200, json=LIST_PAYLOAD))
        # мок: детали по vri_id
        respx.get(f"{ARSHIN_BASE}/vri/{VRI_ID}").mock(
            return_value=httpx.Response(200, json=DETAILS_PAYLOAD)
        )

        data = await fetch_vri_id_by_certificate(client, CERT, year=2025)
        assert data == VRI_ID

        details = await fetch_vri_details(client, VRI_ID)
        line = compose_etalon_line_from_details(details)
        fields = extract_detail_fields(details)

        assert line == (
            "77090.19.1Р.00761951; 77090-19; Преобразователи давления эталонные; ЭЛМЕТРО-Паскаль-04"
        )
        assert fields["organization"].startswith("ФБУ")
        assert fields["vrfDate"] == "15.01.2025"
        assert fields["applicable"] is True


@respx.mock
async def test_fetch_vri_retries_on_server_error():
    async with httpx.AsyncClient() as client:
        route = respx.get(f"{ARSHIN_BASE}/vri").mock(
            side_effect=[
                httpx.Response(500, json={"message": "fail"}),
                httpx.Response(200, json=LIST_PAYLOAD),
            ]
        )
        result = await fetch_vri_id_by_certificate(
            client, CERT, year=2025, sem=None, use_cache=False
        )
        assert result == VRI_ID
        assert route.call_count == 2


@respx.mock
async def test_fetch_vri_prefers_guessed_year():
    cert_2023 = "С-ЕЖБ/04-10-2023/289572783"
    vri_id = "1-289572783"

    # Ответ с year=2023 содержит запись, без year — пусто.
    respx.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert_2023, "year": "2023"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "result": {
                    "count": 1,
                    "items": [
                        {
                            "vri_id": vri_id,
                            "result_docnum": cert_2023,
                            "verification_date": "04.10.2023",
                            "valid_date": "03.10.2026",
                        }
                    ],
                }
            },
        ),
    )
    respx.get(f"{ARSHIN_BASE}/vri", params={"result_docnum": cert_2023}).mock(
        return_value=httpx.Response(200, json={"result": {"count": 0, "items": []}})
    )

    async with httpx.AsyncClient() as client:
        result = await fetch_vri_id_by_certificate(client, cert_2023, use_cache=False)
        assert result == vri_id
