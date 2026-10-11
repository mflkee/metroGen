"""Thin async client for the unified account registry (metroAccounts).

With ``ACCOUNTS_ENABLED`` the registry owns credentials, per-service access flags
and roles; metroGen only keeps its own role and profile.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class AccountsUnavailable(HTTPException):
    def __init__(self, message: str = "Сервис учётных записей недоступен.") -> None:
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=message)


def is_enabled() -> bool:
    return bool(
        settings.ACCOUNTS_ENABLED and settings.ACCOUNTS_URL and settings.ACCOUNTS_SERVICE_TOKEN
    )


def _headers() -> dict[str, str]:
    return {
        "X-Service-Name": settings.ACCOUNTS_SERVICE_NAME,
        "X-Service-Token": settings.ACCOUNTS_SERVICE_TOKEN or "",
    }


async def _request(method: str, path: str, *, json: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{settings.ACCOUNTS_URL.rstrip('/')}/api/v1{path}"
    try:
        async with httpx.AsyncClient(timeout=settings.ACCOUNTS_TIMEOUT_SECONDS) as client:
            response = await client.request(method, url, json=json, headers=_headers())
    except httpx.HTTPError as exc:
        raise AccountsUnavailable() from exc

    if response.status_code >= 500:
        raise AccountsUnavailable()
    if response.status_code >= 400:
        detail = "Ошибка сервиса учётных записей."
        try:
            payload = response.json()
            if isinstance(payload.get("detail"), str):
                detail = payload["detail"]
        except ValueError:
            pass
        raise HTTPException(status_code=response.status_code, detail=detail)
    try:
        return response.json()
    except ValueError as exc:
        raise AccountsUnavailable() from exc


async def verify(*, email: str, password: str) -> dict[str, Any]:
    payload = await _request(
        "POST",
        "/internal/verify",
        json={"email": email, "password": password, "service": settings.ACCOUNTS_SERVICE_NAME},
    )
    account = payload.get("account") or {}
    return {
        "email": account.get("email", email),
        "first_name": account.get("first_name", ""),
        "last_name": account.get("last_name", ""),
        "patronymic": account.get("patronymic"),
        "is_active": account.get("is_active", True),
        "role": payload.get("role"),
    }


async def create_account(
    *,
    email: str,
    first_name: str,
    last_name: str,
    patronymic: str | None,
    role: str | None,
) -> None:
    await _request(
        "POST",
        "/internal/accounts",
        json={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic,
            "service": settings.ACCOUNTS_SERVICE_NAME,
            "role": role,
            "send_invite": True,
        },
    )


async def send_invite(*, email: str) -> None:
    await _request("POST", f"/internal/accounts/{email}/invite")


async def change_password(*, email: str, current_password: str, new_password: str) -> None:
    await _request(
        "POST",
        f"/internal/accounts/{email}/password",
        json={"current_password": current_password, "new_password": new_password},
    )
