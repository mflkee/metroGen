from __future__ import annotations

import asyncio
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.models import User, UserRole
from app.db.repositories import AuxiliaryInstrumentRepository, UserRepository
from app.db.session import get_sessionmaker
from app.services.mappings import _methodology_seed, _org_seed, ensure_methodology, ensure_owner
from app.utils.password_policy import validate_password_policy
from app.utils.security import hash_password

logger = setup_logging()


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
    users = await seed_users(session)
    await session.commit()
    return {
        "owners": owners,
        "methodologies": methodologies,
        "auxiliary_instruments": auxiliary_instruments,
        "users": users,
    }


async def seed_users(session: AsyncSession) -> int:
    repo = UserRepository(session)
    email = settings.BOOTSTRAP_ADMIN_EMAIL.strip().lower()
    if not email:
        return 0

    password = settings.BOOTSTRAP_ADMIN_PASSWORD.strip()
    validate_password_policy(password)

    user = await repo.get_by_email(email)
    if user is None:
        await repo.add(
            User(
                first_name=settings.BOOTSTRAP_ADMIN_FIRST_NAME.strip() or "Bootstrap",
                last_name=settings.BOOTSTRAP_ADMIN_LAST_NAME.strip() or "Administrator",
                patronymic=settings.BOOTSTRAP_ADMIN_PATRONYMIC.strip() or None,
                email=email,
                password_hash=hash_password(password),
                role=UserRole.ADMINISTRATOR,
                is_active=True,
                must_change_password=True,
            )
        )
        logger.warning("Bootstrap administrator %s was created automatically.", email)
        return 1

    changed = False
    if user.role not in {UserRole.DEVELOPER, UserRole.ADMINISTRATOR}:
        user.role = UserRole.ADMINISTRATOR
        changed = True
    if not user.is_active:
        user.is_active = True
        changed = True
    if changed:
        logger.warning("Bootstrap administrator %s was elevated automatically.", email)
    return 1


async def seed_from_config() -> dict[str, int]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        return await seed_database(session)


def seed():
    asyncio.run(seed_from_config())


if __name__ == "__main__":
    seed()
