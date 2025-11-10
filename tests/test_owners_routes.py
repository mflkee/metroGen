import uuid

import pytest


@pytest.mark.anyio
async def test_create_and_update_owner(async_client):
    unique_suffix = uuid.uuid4().hex[:6]
    name = f'ООО "Тест {unique_suffix}"'

    create_payload = {"name": name, "inn": "1234567890"}
    response = await async_client.post("/api/v1/owners", json=create_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == name
    assert body["inn"] == "1234567890"
    owner_id = body["id"]

    update_payload = {"inn": "8901001822"}
    response = await async_client.patch(f"/api/v1/owners/{owner_id}", json=update_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["inn"] == "8901001822"
    assert body["name"] == name

    new_name = f"{name} (обновлено)"
    response = await async_client.patch(f"/api/v1/owners/{owner_id}", json={"name": new_name})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == new_name
    assert body["inn"] == "8901001822"


@pytest.mark.anyio
async def test_create_owner_strips_payload(async_client):
    payload = {"name": "  ООО \"Промтест\"  ", "inn": "  "}
    response = await async_client.post("/api/v1/owners", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == 'ООО "Промтест"'
    assert body["inn"] is None


@pytest.mark.anyio
async def test_update_owner_not_found(async_client):
    response = await async_client.patch("/api/v1/owners/999999", json={"name": "Нет"})
    assert response.status_code == 404
    assert response.json()["detail"] == "owner not found"
