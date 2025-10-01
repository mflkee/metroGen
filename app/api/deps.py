from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import httpx

from app.core.config import settings
from app.db.session import get_db

__all__ = ("get_http_client", "get_semaphore", "get_db")

# Глобальный семафор для ограничения параллельности исходящих запросов
_SEM = asyncio.Semaphore(settings.ARSHIN_CONCURRENCY)


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """Возвращает новый httpx.AsyncClient на время обработки запроса.

    Такой подход упрощает тестирование с respx (моки подхватываются всегда)
    и не создаёт зависимостей от времени импорта.
    """
    async with httpx.AsyncClient(
        headers={"User-Agent": settings.USER_AGENT},
        timeout=settings.ARSHIN_TIMEOUT,
    ) as client:
        yield client


def get_semaphore() -> asyncio.Semaphore:
    """Возвращает общий семафор для ограничения параллельности."""
    return _SEM
