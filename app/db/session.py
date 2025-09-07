from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _get_database_url() -> str:
    url = getattr(settings, "DATABASE_URL", None)
    if not url:
        # default to local sqlite for development
        return "sqlite+aiosqlite:///./dev.db"
    return url


def get_engine() -> AsyncEngine:
    return create_async_engine(_get_database_url(), future=True)


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    engine = get_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields AsyncSession."""
    async_session = get_sessionmaker()
    async with async_session() as session:
        yield session
