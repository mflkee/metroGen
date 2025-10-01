from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

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


async def seed_database(session: AsyncSession) -> dict[str, int]:
    """Populate the relational database with seed data from JSON files."""

    owners = await seed_owners(session)
    methodologies = await seed_methodologies(session)
    await session.commit()
    return {"owners": owners, "methodologies": methodologies}


async def seed_from_config() -> dict[str, int]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        return await seed_database(session)


def seed():
    asyncio.run(seed_from_config())


if __name__ == "__main__":
    seed()
