from __future__ import annotations

import asyncio
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import AuxiliaryInstrumentRepository
from app.db.session import get_sessionmaker
from app.services.mappings import _methodology_seed, _org_seed, ensure_methodology, ensure_owner


async def seed_owners(session: AsyncSession) -> int:
    count = 0
    for name, payload in _org_seed().items():
        owner = await ensure_owner(
            session,
            name,
            inn_hint=str(payload.get("inn") or "") or None,
            aliases=(payload.get("aliases") or [name]),
        )
        if owner is not None:
            count += 1
    return count


async def seed_methodologies(session: AsyncSession) -> int:
    count = 0
    for code in _methodology_seed().keys():
        methodology = await ensure_methodology(session, code)
        if methodology is not None:
            count += 1
    return count


async def seed_auxiliary_instruments(session: AsyncSession) -> int:
    repo = AuxiliaryInstrumentRepository(session)
    items = [
        {
            "title": "Измерители влажности и температуры",
            "reg_number": "71394-18",
            "modification": "ИВТМ-7 М5-Д",
            "manufacture_num": "96320",
            "certificate_no": "С-ВСА/02-06-2025/436974158",
            "verification_date": date(2025, 6, 2),
            "valid_to": date(2026, 6, 1),
        },
        {
            "title": "Измерители влажности и температуры",
            "reg_number": "71394-18",
            "modification": "ИВТМ-7 М5-Д",
            "manufacture_num": "83243",
            "certificate_no": "С-ВЯ/22-05-2025/436102986",
            "verification_date": date(2025, 5, 22),
            "valid_to": date(2026, 5, 21),
        },
        {
            "title": "Секундомер электронный",
            "reg_number": "44154-20",
            "modification": "Интеграл С-01",
            "manufacture_num": "419433",
            "certificate_no": "С-ВЯ/22-01-2026/497053091",
            "verification_date": date(2026, 1, 22),
            "valid_to": date(2027, 1, 21),
        },
        {
            "title": "Мультиметры цифровые",
            "reg_number": "77699-20",
            "modification": "АКИП-2203/1",
            "manufacture_num": "21190145",
            "certificate_no": "С-ВЯ/28-01-2025/405670101",
            "verification_date": date(2025, 1, 28),
            "valid_to": date(2026, 1, 27),
        },
    ]

    count = 0
    for item in items:
        await repo.upsert_instrument(
            reg_number=item["reg_number"],
            manufacture_num=item["manufacture_num"],
            values={
                "title": item["title"],
                "modification": item["modification"],
                "certificate_no": item["certificate_no"],
                "verification_date": item["verification_date"],
                "valid_to": item["valid_to"],
            },
        )
        count += 1
    return count


async def seed_database(session: AsyncSession) -> dict[str, int]:
    """Populate the relational database with seed data from JSON files."""

    owners = await seed_owners(session)
    methodologies = await seed_methodologies(session)
    auxiliary_instruments = await seed_auxiliary_instruments(session)
    await session.commit()
    return {
        "owners": owners,
        "methodologies": methodologies,
        "auxiliary_instruments": auxiliary_instruments,
    }


async def seed_from_config() -> dict[str, int]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        return await seed_database(session)


def seed():
    asyncio.run(seed_from_config())


if __name__ == "__main__":
    seed()
