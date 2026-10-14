"""Route-level coverage for the reference CRUD and the form mapping rules.

These hit the real app with the test database (see ``tests/conftest.py``). Each test uses a
unique suffix so a run leaves no collisions behind.
"""

import uuid

import pytest


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


@pytest.mark.anyio
async def test_owner_aliases_are_replaced_and_the_owner_can_be_deleted(async_client):
    suffix = _suffix()
    name = f'ООО "Алиасы {suffix}"'

    created = await async_client.post("/api/v1/owners", json={"name": name, "inn": "7700000000"})
    assert created.status_code == 201
    owner_id = created.json()["id"]
    assert created.json()["aliases"] == []

    replaced = await async_client.put(
        f"/api/v1/owners/{owner_id}/aliases",
        json={"aliases": [f"Алиас-1 {suffix}", f"Алиас-2 {suffix}"]},
    )
    assert replaced.status_code == 200
    aliases = replaced.json()["aliases"]
    assert f"Алиас-1 {suffix}" in aliases
    assert f"Алиас-2 {suffix}" in aliases

    cleared = await async_client.put(f"/api/v1/owners/{owner_id}/aliases", json={"aliases": []})
    assert cleared.status_code == 200
    assert cleared.json()["aliases"] == []

    deleted = await async_client.delete(f"/api/v1/owners/{owner_id}")
    assert deleted.status_code == 204

    missing = await async_client.delete(f"/api/v1/owners/{owner_id}")
    assert missing.status_code == 404


@pytest.mark.anyio
async def test_methodology_aliases_and_delete(async_client):
    suffix = _suffix()
    code = f"МИ {suffix}"

    created = await async_client.post(
        "/api/v1/methodologies",
        json={
            "code": code,
            "title": f"Методика {suffix}",
            "allowable_variation_pct": 1.5,
            "points": [
                {
                    "position": 1,
                    "label": "8.1",
                    "point_type": "clause",
                    "default_text": "Внешний осмотр",
                }
            ],
        },
    )
    assert created.status_code == 201
    methodology_id = created.json()["id"]
    assert created.json()["aliases"] == []

    replaced = await async_client.put(
        f"/api/v1/methodologies/{methodology_id}/aliases",
        json={"aliases": [f"Псевдоним {suffix}"]},
    )
    assert replaced.status_code == 200
    assert f"Псевдоним {suffix}" in replaced.json()["aliases"]

    deleted = await async_client.delete(f"/api/v1/methodologies/{methodology_id}")
    assert deleted.status_code == 204


@pytest.mark.anyio
async def test_auxiliary_instrument_update_and_delete(async_client):
    suffix = _suffix()
    created = await async_client.post(
        "/api/v1/auxiliary-instruments",
        json={
            "title": f"Термометр {suffix}",
            "reg_number": f"11111-{suffix[:2]}",
            "manufacture_num": f"SN-{suffix}",
        },
    )
    assert created.status_code == 201
    instrument_id = created.json()["id"]

    updated = await async_client.patch(
        f"/api/v1/auxiliary-instruments/{instrument_id}",
        json={"modification": "М1"},
    )
    assert updated.status_code == 200
    assert updated.json()["modification"] == "М1"

    deleted = await async_client.delete(f"/api/v1/auxiliary-instruments/{instrument_id}")
    assert deleted.status_code == 204


@pytest.mark.anyio
async def test_etalon_update_certificates_and_delete(async_client):
    suffix = _suffix()
    reg_number = f"77090.19.2Р.{suffix}"

    created = await async_client.post(
        "/api/v1/etalons",
        json={"reg_number": reg_number, "title": f"Эталон {suffix}"},
    )
    assert created.status_code == 201
    etalon_id = created.json()["id"]

    updated = await async_client.patch(f"/api/v1/etalons/{etalon_id}", json={"rank_code": "2Р"})
    assert updated.status_code == 200
    assert updated.json()["rank_code"] == "2Р"

    added = await async_client.post(
        f"/api/v1/etalons/{etalon_id}/certifications",
        json={"certificate_no": f"СВ-{suffix}", "valid_to": "2030-01-01"},
    )
    assert added.status_code == 201
    certification_id = added.json()["id"]

    listed = await async_client.get(f"/api/v1/etalons/{etalon_id}/certifications")
    assert listed.status_code == 200
    assert any(cert["id"] == certification_id for cert in listed.json())

    removed = await async_client.delete(
        f"/api/v1/etalons/{etalon_id}/certifications/{certification_id}"
    )
    assert removed.status_code == 204

    deleted = await async_client.delete(f"/api/v1/etalons/{etalon_id}")
    assert deleted.status_code == 204


@pytest.mark.anyio
async def test_template_catalog_and_rule_crud(async_client):
    catalog = await async_client.get("/api/v1/templates")
    assert catalog.status_code == 200
    body = catalog.json()
    template_ids = {item["id"] for item in body["templates"]}
    assert {"pressure_common", "level_meter", "level_meter_two_tables"} <= template_ids
    assert "manometers" in body["instrument_kinds"]
    assert "mitype_number" in body["match_fields"]


@pytest.mark.anyio
async def test_template_rule_drives_the_preview(async_client):
    suffix = _suffix()
    mitype_number = f"TEST-{suffix}"

    created = await async_client.post(
        "/api/v1/templates/rules",
        json={
            "instrument_kind": "manometers",
            "match_field": "mitype_number",
            "match_value": mitype_number,
            "template_id": "pressure_sensor",
            "priority": 5,
            "is_active": True,
        },
    )
    assert created.status_code == 201
    rule_id = created.json()["id"]

    preview = await async_client.post(
        "/api/v1/templates/rules/preview",
        json={"instrument_kind": "manometers", "mitype_number": mitype_number},
    )
    assert preview.status_code == 200
    assert preview.json()["template_id"] == "pressure_sensor"
    assert preview.json()["source"] == "rule"
    assert preview.json()["rule_id"] == rule_id

    disabled = await async_client.patch(
        f"/api/v1/templates/rules/{rule_id}", json={"is_active": False}
    )
    assert disabled.status_code == 200
    assert disabled.json()["is_active"] is False

    fallback = await async_client.post(
        "/api/v1/templates/rules/preview",
        json={"instrument_kind": "manometers", "mitype_number": mitype_number},
    )
    assert fallback.status_code == 200
    assert fallback.json()["source"] == "fallback"

    deleted = await async_client.delete(f"/api/v1/templates/rules/{rule_id}")
    assert deleted.status_code == 204


@pytest.mark.anyio
async def test_template_rule_rejects_unknown_template(async_client):
    response = await async_client.post(
        "/api/v1/templates/rules",
        json={
            "instrument_kind": "manometers",
            "match_field": "mitype_number",
            "match_value": "X",
            "template_id": "no_such_template",
            "priority": 5,
        },
    )
    assert response.status_code == 400
