from datetime import date

import pytest
from sqlalchemy import delete, select

from app.db import models
from app.db.session import get_sessionmaker
from app.services.registry_ingest import ingest_registry_rows


@pytest.mark.anyio
async def test_ingest_registry_rows_persists_owner_and_methodology():
    sessionmaker = get_sessionmaker()
    source_file = "test_ingest_registry.xlsx"
    owner_name = 'ООО "Тест Инжиниринг"'
    owner_inn = "1234567890"
    methodology_code = "МИ 2124-90"
    serial = " 03607 "

    rows = [
        {
            "Заводской №/ Буквенно-цифровое обозначение": serial,
            "Документ": "С-ЕЖБ/05-06-2025/443771099",
            "номер_протокола": "06/001/25",
            "Владелец СИ": owner_name,
            "ИНН": owner_inn,
            "Методика поверки": methodology_code,
            "Дата поверки": date(2025, 6, 5),
            "Действительно до": date(2026, 6, 4),
        }
    ]

    async with sessionmaker() as session:
        # cleanup in case of previous runs
        await session.execute(
            delete(models.VerificationRegistryEntry).where(
                models.VerificationRegistryEntry.source_file == source_file
            )
        )
        await session.execute(delete(models.Owner).where(models.Owner.name == owner_name))
        await session.commit()

        result = await ingest_registry_rows(
            session,
            source_file=source_file,
            rows=rows,
            source_sheet="tests",
        )

        assert result["processed"] == 1

        entry = (
            await session.execute(
                select(models.VerificationRegistryEntry).where(
                    models.VerificationRegistryEntry.source_file == source_file
                )
            )
        ).scalar_one()
        assert entry.normalized_serial == "03607"
        assert entry.document_no == "С-ЕЖБ/05-06-2025/443771099"

        owner = (
            await session.execute(select(models.Owner).where(models.Owner.name == owner_name))
        ).scalar_one()
        assert owner.inn == owner_inn

        methodology = (
            await session.execute(
                select(models.Methodology).where(models.Methodology.code == methodology_code)
            )
        ).scalar_one()
        assert methodology.allowable_variation_pct == pytest.approx(1.5)

        points = (
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
        point_labels = [point.label for point in points]
        assert "5.1" in point_labels
        assert "5.2.3" in point_labels

        # cleanup created data for isolation
        await session.execute(
            delete(models.VerificationRegistryEntry).where(
                models.VerificationRegistryEntry.source_file == source_file
            )
        )
        await session.execute(delete(models.Owner).where(models.Owner.name == owner_name))
        await session.commit()
