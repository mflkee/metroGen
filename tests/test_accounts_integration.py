from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.db.models import User, UserRole
from app.schemas.auth import LoginRequest
from app.services import accounts_client
from app.services.auth_service import AuthService


def _enable_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ACCOUNTS_ENABLED", True)
    monkeypatch.setattr(settings, "ACCOUNTS_URL", "http://registry:8000")
    monkeypatch.setattr(settings, "ACCOUNTS_SERVICE_TOKEN", "service-token")


def test_accounts_client_calls_the_versioned_internal_path(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_registry(monkeypatch)
    captured: dict = {}

    class _Response:
        status_code = 200

        def json(self) -> dict:
            return {"ok": True, "account": {"email": "x@mkair.ru"}, "role": "MKAIR"}

    class _Client:
        def __init__(self, **_kwargs) -> None:
            pass

        async def __aenter__(self) -> _Client:
            return self

        async def __aexit__(self, *_exc) -> None:
            return None

        async def request(self, method: str, url: str, **kwargs):
            captured["method"] = method
            captured["url"] = url
            captured["headers"] = kwargs.get("headers")
            return _Response()

    monkeypatch.setattr(accounts_client.httpx, "AsyncClient", _Client)

    import asyncio

    result = asyncio.run(accounts_client.verify(email="x@mkair.ru", password="secret"))

    assert captured["method"] == "POST"
    assert captured["url"].endswith("/api/v1/internal/verify")
    assert captured["headers"]["X-Service-Name"] == "metrogen"
    assert result["role"] == "MKAIR"


class _DummySession:
    async def commit(self) -> None:
        return None

    async def refresh(self, _obj: object) -> None:
        return None


def _patch_repository(monkeypatch: pytest.MonkeyPatch, existing: User | None) -> None:
    class _StubUsers:
        def __init__(self, _session: object) -> None:
            pass

        async def get_by_email(self, _email: str) -> User | None:
            return existing

        async def add(self, user: User) -> User:
            return user

    monkeypatch.setattr("app.services.auth_service.UserRepository", _StubUsers)


@pytest.mark.asyncio
async def test_login_via_registry_provisions_user(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_registry(monkeypatch)
    _patch_repository(monkeypatch, None)

    async def fake_verify(**_kwargs) -> dict:
        return {
            "email": "new@mkair.ru",
            "first_name": "Новый",
            "last_name": "Сотрудник",
            "patronymic": None,
            "is_active": True,
            "role": "ADMINISTRATOR",
        }

    monkeypatch.setattr(accounts_client, "verify", fake_verify)

    user, token = await AuthService(_DummySession()).login(
        LoginRequest(email="new@mkair.ru", password="Whatever-1")
    )

    assert user.role is UserRole.ADMINISTRATOR
    assert user.password_hash == "!"
    assert token


@pytest.mark.asyncio
async def test_login_via_registry_syncs_role(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_registry(monkeypatch)
    existing = User(
        first_name="Старый",
        last_name="Сотрудник",
        email="old@mkair.ru",
        password_hash="!",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    _patch_repository(monkeypatch, existing)

    async def fake_verify(**_kwargs) -> dict:
        return {"email": "old@mkair.ru", "is_active": True, "role": "MKAIR"}

    monkeypatch.setattr(accounts_client, "verify", fake_verify)

    user, _token = await AuthService(_DummySession()).login(
        LoginRequest(email="old@mkair.ru", password="Whatever-1")
    )
    assert user.role is UserRole.MKAIR


@pytest.mark.asyncio
async def test_login_via_registry_propagates_denial(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_registry(monkeypatch)
    _patch_repository(monkeypatch, None)

    async def deny(**_kwargs) -> dict:
        raise HTTPException(status_code=403, detail="Нет доступа к сервису «metrogen».")

    monkeypatch.setattr(accounts_client, "verify", deny)

    with pytest.raises(HTTPException) as excinfo:
        await AuthService(_DummySession()).login(
            LoginRequest(email="new@mkair.ru", password="Whatever-1")
        )
    assert excinfo.value.status_code == 403


@pytest.mark.asyncio
async def test_change_password_goes_through_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_registry(monkeypatch)
    user = User(
        first_name="Тест",
        last_name="Тестов",
        email="user@mkair.ru",
        password_hash="!",
        role=UserRole.MKAIR,
        is_active=True,
    )

    calls: list[dict] = []

    async def fake_change(**kwargs) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(accounts_client, "change_password", fake_change)

    from app.schemas.auth import ChangePasswordRequest

    await AuthService(_DummySession()).change_password(
        user=user,
        payload=ChangePasswordRequest(
            current_password="Old-Pass-1",
            new_password="New-Pass-1",
            confirm_new_password="New-Pass-1",
        ),
    )

    assert calls and calls[0]["email"] == "user@mkair.ru"
    assert calls[0]["new_password"] == "New-Pass-1"
    assert user.must_change_password is False
