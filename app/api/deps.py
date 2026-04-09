from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import User, UserRole
from app.db.repositories import UserRepository
from app.db.session import get_db
from app.utils.security import decode_access_token

__all__ = (
    "AdminUser",
    "BearerCredentials",
    "CurrentUser",
    "DbSession",
    "get_db",
    "get_http_client",
    "get_semaphore",
)

# Глобальный семафор для ограничения параллельности исходящих запросов
_SEM = asyncio.Semaphore(settings.ARSHIN_CONCURRENCY)
bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[AsyncSession, Depends(get_db)]
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """Возвращает новый httpx.AsyncClient на время обработки запроса.

    Такой подход упрощает тестирование с respx (моки подхватываются всегда)
    и не создаёт зависимостей от времени импорта.
    """
    timeout = httpx.Timeout(
        timeout=settings.ARSHIN_TIMEOUT,
        connect=settings.ARSHIN_TIMEOUT,
        read=settings.ARSHIN_TIMEOUT,
        write=settings.ARSHIN_TIMEOUT,
        pool=settings.ARSHIN_TIMEOUT,
    )
    limits = httpx.Limits(
        max_connections=settings.ARSHIN_CONCURRENCY * 2,
        max_keepalive_connections=settings.ARSHIN_CONCURRENCY,
    )
    async with httpx.AsyncClient(
        headers={"User-Agent": settings.USER_AGENT},
        timeout=timeout,
        limits=limits,
    ) as client:
        yield client


def get_semaphore() -> asyncio.Semaphore:
    """Возвращает общий семафор для ограничения параллельности."""
    return _SEM


async def get_current_user(
    db: DbSession,
    credentials: BearerCredentials,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    try:
        payload = decode_access_token(credentials.credentials, settings.SECRET_KEY)
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is invalid.",
        ) from exc

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not available.",
        )

    now = datetime.now(tz=UTC)
    last_seen_at = _coerce_utc(user.last_seen_at)
    if last_seen_at is None or now - last_seen_at >= timedelta(minutes=5):
        user.last_seen_at = now
        await db.commit()
        await db.refresh(user)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_admin(current_user: CurrentUser) -> User:
    if not has_admin_access(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator or developer role is required.",
        )
    return current_user


AdminUser = Annotated[User, Depends(require_admin)]


def has_admin_access(role: UserRole | str | None) -> bool:
    return role in {UserRole.DEVELOPER, UserRole.ADMINISTRATOR, "DEVELOPER", "ADMINISTRATOR"}


def has_operator_access(role: UserRole | str | None) -> bool:
    return has_admin_access(role) or role in {UserRole.MKAIR, "MKAIR"}


def _coerce_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
