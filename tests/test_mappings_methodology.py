import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.repositories import MethodologyPointPayload, MethodologyRepository
from app.services.mappings import resolve_methodology


@pytest.mark.anyio
async def test_resolve_methodology_via_partial_alias_loads_points():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_maker() as session:
        repo = MethodologyRepository(session)
        methodology = await repo.upsert_methodology(
            code="МИ 1234-2025",
            title="МИ 1234-2025",
        )
        await repo.ensure_aliases(
            methodology,
            [
                ("МИ 1234-2025", 100),
            ],
        )
        await repo.replace_points(
            methodology,
            [
                MethodologyPointPayload(position=1, label="5.1"),
                MethodologyPointPayload(position=2, label="5.2"),
            ],
        )
        await session.commit()

        info = await resolve_methodology(session, "МИ 1234")

        assert info is not None
        assert info.code == "МИ 1234-2025"
        assert [item.code for item in info.point_items] == ["5.1", "5.2"]

    await engine.dispose()
