from __future__ import annotations

import pytest
from sqlalchemy import delete, select

from app.db import models
from app.db.session import get_sessionmaker


@pytest.mark.anyio
async def test_create_and_list_auxiliary_instruments(async_client):
    payload = {
        "title": "Измеритель влажности и температуры",
        "reg_number": "71394-18",
        "modification": "ИВТМ-7",
        "manufacture_num": "96320",
        "certificate_no": "С-ВСА/02-06-2025/436974158",
        "verification_date": "02.06.2025",
        "valid_to": "01.06.2026",
    }

    response = await async_client.post("/api/v1/auxiliary-instruments", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["reg_number"] == payload["reg_number"]
    assert body["verification_date"] == "2025-06-02"
    assert body["valid_to"] == "2026-06-01"

    list_response = await async_client.get("/api/v1/auxiliary-instruments")
    assert list_response.status_code == 200
    items = list_response.json()
    assert any(
        item["reg_number"] == payload["reg_number"]
        and item["manufacture_num"] == payload["manufacture_num"]
        for item in items
    )

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await session.execute(
            delete(models.AuxiliaryVerificationInstrument).where(
                models.AuxiliaryVerificationInstrument.reg_number == payload["reg_number"],
                models.AuxiliaryVerificationInstrument.normalized_serial
                == payload["manufacture_num"],
            )
        )
        await session.commit()


@pytest.mark.anyio
async def test_create_auxiliary_instrument_upserts_by_reg_and_serial(async_client):
    first = {
        "title": "Секундомер электронный",
        "reg_number": "44154-16",
        "modification": "Интеграл С-01",
        "manufacture_num": "419433",
        "certificate_no": "CERT-1",
    }
    second = {
        **first,
        "certificate_no": "CERT-2",
        "valid_to": "2025-12-18",
    }

    response1 = await async_client.post("/api/v1/auxiliary-instruments", json=first)
    assert response1.status_code == 201
    id1 = response1.json()["id"]

    response2 = await async_client.post("/api/v1/auxiliary-instruments", json=second)
    assert response2.status_code == 201
    body2 = response2.json()
    assert body2["id"] == id1
    assert body2["certificate_no"] == "CERT-2"
    assert body2["valid_to"] == "2025-12-18"

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        rows = (
            (
                await session.execute(
                    select(models.AuxiliaryVerificationInstrument).where(
                        models.AuxiliaryVerificationInstrument.reg_number == first["reg_number"],
                        models.AuxiliaryVerificationInstrument.normalized_serial
                        == first["manufacture_num"],
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1
        assert rows[0].certificate_no == "CERT-2"

        await session.execute(
            delete(models.AuxiliaryVerificationInstrument).where(
                models.AuxiliaryVerificationInstrument.reg_number == first["reg_number"],
                models.AuxiliaryVerificationInstrument.normalized_serial
                == first["manufacture_num"],
            )
        )
        await session.commit()


@pytest.mark.anyio
async def test_bulk_upsert_auxiliary_instruments_replace_all(async_client):
    base_items = [
        {
            "title": "Aux One",
            "reg_number": "99999-01",
            "modification": "M1",
            "manufacture_num": "S001",
            "certificate_no": "CERT-1",
        },
        {
            "title": "Aux Two",
            "reg_number": "99999-02",
            "modification": "M2",
            "manufacture_num": "S002",
            "certificate_no": "CERT-2",
        },
    ]
    seed_response = await async_client.post(
        "/api/v1/auxiliary-instruments/bulk",
        json={"items": base_items, "replace_all": True},
    )
    assert seed_response.status_code == 200
    assert seed_response.json()["upserted"] == 2

    updated_items = [
        {
            "title": "Aux Two Updated",
            "reg_number": "99999-02",
            "modification": "M2",
            "manufacture_num": "S002",
            "certificate_no": "CERT-2B",
        }
    ]
    replace_response = await async_client.post(
        "/api/v1/auxiliary-instruments/bulk",
        json={"items": updated_items, "replace_all": True},
    )
    assert replace_response.status_code == 200
    summary = replace_response.json()
    assert summary["upserted"] == 1
    assert summary["deleted"] >= 1

    list_response = await async_client.get("/api/v1/auxiliary-instruments")
    assert list_response.status_code == 200
    rows = [
        row
        for row in list_response.json()
        if row["reg_number"].startswith("99999-")
    ]
    assert len(rows) == 1
    assert rows[0]["reg_number"] == "99999-02"
    assert rows[0]["certificate_no"] == "CERT-2B"

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await session.execute(
            delete(models.AuxiliaryVerificationInstrument).where(
                models.AuxiliaryVerificationInstrument.reg_number.in_(["99999-01", "99999-02"])
            )
        )
        await session.commit()
