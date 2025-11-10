import pytest
from sqlalchemy import delete, select

from app.db import models
from app.db.session import get_sessionmaker


@pytest.mark.anyio
async def test_create_methodology_endpoint(async_client):
    payload = {
        "code": "МИ 9999-99",
        "title": "Методика поверки датчиков давления",
        "aliases": ["9999-99 МИ"],
        "points": [
            {"position": 1, "label": "Соответствует/не соответствует"},
            {"position": 2, "label": "Температура ____ °C"},
        ],
    }

    response = await async_client.post("/api/v1/methodologies", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == payload["code"]
    assert body["title"] == payload["title"]
    assert len(body["points"]) == 2
    assert body["points"][0]["point_type"] == "bool"
    assert body["points"][1]["point_type"] == "custom"

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        methodology = (
            await session.execute(
                select(models.Methodology).where(models.Methodology.code == payload["code"])
            )
        ).scalar_one()
        assert methodology.title == payload["title"]
        stored_points = (
            (
                await session.execute(
                    select(models.MethodologyPoint)
                    .where(models.MethodologyPoint.methodology_id == methodology.id)
                    .order_by(models.MethodologyPoint.position)
                )
            )
            .scalars()
            .all()
        )
        assert len(stored_points) == 2
        assert stored_points[0].point_type == "bool"
        assert stored_points[1].point_type == "custom"

        await session.execute(
            delete(models.MethodologyPoint).where(
                models.MethodologyPoint.methodology_id == methodology.id
            )
        )
        await session.execute(
            delete(models.Methodology).where(models.Methodology.id == methodology.id)
        )
        await session.commit()


@pytest.mark.anyio
async def test_create_methodology_variant_with_extra_point(async_client):
    long_title = (
        "МИ 2124-90 «ГСИ. Манометры, вакуумметры, мановакуумметры, "
        "напоромеры, тягомеры и тягонапоромеры показывающие и "
        "самопишущие. Методика поверки»"
    )
    payload = {
        "code": "МИ 2124-91",
        "title": long_title,
        "aliases": ["2124-91 МИ"],
        "allowable_variation_pct": 1.5,
        "points": [
            {"position": 1, "label": "5.1"},
            {"position": 2, "label": "5.2.3"},
            {"position": 3, "label": "5.3"},
            {"position": 4, "label": "Проведение очистки _____"},
        ],
    }

    response = await async_client.post("/api/v1/methodologies", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == payload["code"]
    assert body["points"][3]["point_type"] == "custom"

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        methodology = (
            await session.execute(
                select(models.Methodology).where(models.Methodology.code == payload["code"])
            )
        ).scalar_one()
        aliases = (
            (
                await session.execute(
                    select(models.MethodologyAlias.alias).where(
                        models.MethodologyAlias.methodology_id == methodology.id
                    )
                )
            )
            .scalars()
            .all()
        )
        assert "2124-91 МИ" in aliases

        await session.execute(
            delete(models.MethodologyPoint).where(
                models.MethodologyPoint.methodology_id == methodology.id
            )
        )
        await session.execute(
            delete(models.MethodologyAlias).where(
                models.MethodologyAlias.methodology_id == methodology.id
            )
        )
        await session.execute(
            delete(models.Methodology).where(models.Methodology.id == methodology.id)
        )
        await session.commit()


@pytest.mark.anyio
async def test_create_methodology_with_explicit_point_types(async_client):
    payload = {
        "code": "МИ 8888-88",
        "title": "Методика с явным типом",
        "points": [
            {"position": 1, "label": "Проверка параметров", "point_type": "clause"},
            {"position": 2, "label": "Соответствует", "point_type": "bool"},
        ],
    }

    response = await async_client.post("/api/v1/methodologies", json=payload)
    assert response.status_code == 201


@pytest.mark.anyio
async def test_create_methodology_requires_points(async_client):
    payload = {"code": "МИ 0000-00", "title": "Без точек", "points": []}
    response = await async_client.post("/api/v1/methodologies", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "points are required"


@pytest.mark.anyio
async def test_create_methodology_rejects_empty_labels(async_client):
    payload = {
        "code": "МИ 0001-00",
        "title": "Пустые точки",
        "points": [{"position": 1, "label": "   "}],
    }
    response = await async_client.post("/api/v1/methodologies", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "at least one point must have non-empty label"
