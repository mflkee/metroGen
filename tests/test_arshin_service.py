import respx
import httpx

from app.services.arshin_client import (
    fetch_vri_id_by_certificate,
    fetch_vri_details,
    compose_etalon_line_from_details,
    extract_detail_fields,
    ARSHIN_BASE,
)

CERT = "С-ВЯ/15-01-2025/402123271"
VRI_ID = "1-402123271"

LIST_PAYLOAD = {
    "result": {
        "count": 1, "start": 0, "rows": 10,
        "items": [{
            "vri_id": VRI_ID,
            "org_title": "ФБУ \"ТЮМЕНСКИЙ ЦСМ\"",
            "mit_number": "77090-19",
            "mit_title": "Преобразователи давления эталонные",
            "mit_notation": "ЭЛМЕТРО-Паскаль-04, Паскаль-04",
            "mi_modification": "1М-0,01-Т35",
            "mi_number": "3127",
            "verification_date": "15.01.2025",
            "valid_date": "14.01.2026",
            "result_docnum": CERT,
            "applicability": True
        }]
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
            "organization": "ФБУ \"ТЮМЕНСКИЙ ЦСМ\"",
            "vrfDate": "15.01.2025",
            "validDate": "14.01.2026",
            "applicable": {"certNum": CERT}
        },
        "info": {
            "protocol_url": f"{ARSHIN_BASE}/vri/{VRI_ID}/protocol"
        }
    }
}

@respx.mock
async def test_fetch_vri_and_details():
    async with httpx.AsyncClient() as client:
        # мок: список по сертификату
        respx.get(f"{ARSHIN_BASE}/vri").mock(
            return_value=httpx.Response(200, json=LIST_PAYLOAD)
        )
        # мок: детали по vri_id
        respx.get(f"{ARSHIN_BASE}/vri/{VRI_ID}").mock(
            return_value=httpx.Response(200, json=DETAILS_PAYLOAD)
        )

        data = await fetch_vri_id_by_certificate(client, CERT, year=2025)
        assert data["vri_id"] == VRI_ID

        details = await fetch_vri_details(client, VRI_ID)
        line = compose_etalon_line_from_details(details)
        fields = extract_detail_fields(details)

        assert line == "77090.19.1Р.00761951; 77090-19; Преобразователи давления эталонные; ЭЛМЕТРО-Паскаль-04"
        assert fields["organization"].startswith("ФБУ")
        assert fields["vrfDate"] == "15.01.2025"
        assert fields["applicable"] is True
