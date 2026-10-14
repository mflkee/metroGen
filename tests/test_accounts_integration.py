from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.db.models import User, UserRole
from app.schemas.auth import LoginRequest
from app.schemas.user import UserUpdateRequest
from app.services import accounts_client
from app.services.auth_service import AuthService
from app.services.user_service import UserService


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


class _CountingSession:
    """A session that only remembers whether anything was written."""

    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1

    async def refresh(self, _obj: object) -> None:
        return None


def _registry_listing(
    email: str = "target@mkair.ru",
    role: str = "ADMINISTRATOR",
    *,
    service_active: bool = True,
    stamp: str | None = "2026-10-14T05:43:35.451482Z",
) -> list[dict]:
    """What `GET /internal/accounts` returns: accounts with their per-service grants."""

    return [
        {
            "email": email,
            "first_name": "Цель",
            "last_name": "Тест",
            "patronymic": None,
            "is_active": True,
            "services": [
                {
                    "service": settings.ACCOUNTS_SERVICE_NAME,
                    "role": role,
                    "is_active": service_active,
                    "role_updated_at": stamp,
                }
            ],
        }
    ]


def _stub_user_repository(monkeypatch: pytest.MonkeyPatch, users: list[User]) -> None:
    class _StubUsers:
        def __init__(self, _session: object) -> None:
            pass

        async def list_all(self, search: str | None = None) -> list[User]:
            return users

        async def get_by_id(self, user_id: int) -> User | None:
            return next((user for user in users if user.id == user_id), users[0] if users else None)

        async def get_by_id_for_update(self, user_id: int) -> User | None:
            return await self.get_by_id(user_id)

    monkeypatch.setattr("app.services.user_service.UserRepository", _StubUsers)


def _local_user(**overrides) -> User:
    fields = {
        "first_name": "Цель",
        "last_name": "Тест",
        "email": "target@mkair.ru",
        "password_hash": "!",
        "role": UserRole.CUSTOMER,
        "is_active": True,
    }
    fields.update(overrides)
    return User(**fields)


@pytest.mark.asyncio
async def test_user_list_takes_the_role_from_the_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """A role changed in the console shows up on the next page load, not at the next login."""

    _enable_registry(monkeypatch)
    user = _local_user()
    _stub_user_repository(monkeypatch, [user])

    async def fake_list() -> list[dict]:
        return _registry_listing(role="ADMINISTRATOR")

    monkeypatch.setattr(accounts_client, "list_accounts", fake_list)

    session = _CountingSession()
    listed = await UserService(session).list_users()

    assert listed == [user]
    assert user.role is UserRole.ADMINISTRATOR
    assert session.commits == 1


@pytest.mark.asyncio
async def test_user_list_ignores_an_account_it_does_not_know(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rows the registry has never heard of (service accounts, tests) keep their role."""

    _enable_registry(monkeypatch)
    user = _local_user(email="service@metrogen.local", role=UserRole.DEVELOPER)
    _stub_user_repository(monkeypatch, [user])

    async def fake_list() -> list[dict]:
        return _registry_listing(email="someone-else@mkair.ru")

    monkeypatch.setattr(accounts_client, "list_accounts", fake_list)

    session = _CountingSession()
    await UserService(session).list_users()

    assert user.role is UserRole.DEVELOPER
    assert session.commits == 0


@pytest.mark.asyncio
async def test_user_list_survives_a_registry_outage(monkeypatch: pytest.MonkeyPatch) -> None:
    """A page load is not the place to fail: the local copy is served instead."""

    _enable_registry(monkeypatch)
    user = _local_user(role=UserRole.MKAIR)
    _stub_user_repository(monkeypatch, [user])

    async def unavailable() -> list[dict]:
        raise accounts_client.AccountsUnavailable()

    monkeypatch.setattr(accounts_client, "list_accounts", unavailable)

    session = _CountingSession()
    listed = await UserService(session).list_users()

    assert listed == [user]
    assert user.role is UserRole.MKAIR
    assert session.commits == 0


@pytest.mark.asyncio
async def test_user_list_survives_a_registry_that_does_not_know_the_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deploy order is not a trap: a registry older than this service still opens the page."""

    _enable_registry(monkeypatch)
    user = _local_user(role=UserRole.MKAIR)
    _stub_user_repository(monkeypatch, [user])

    async def older_registry() -> list[dict]:
        raise HTTPException(status_code=404, detail="Not Found")

    monkeypatch.setattr(accounts_client, "list_accounts", older_registry)

    session = _CountingSession()
    listed = await UserService(session).list_users()

    assert listed == [user]
    assert user.role is UserRole.MKAIR
    assert session.commits == 0


@pytest.mark.asyncio
async def test_role_update_is_written_into_the_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """The registry owns the role: a change here is written there, not only kept locally."""

    _enable_registry(monkeypatch)
    user = _local_user()
    _stub_user_repository(monkeypatch, [user])

    written: list[dict] = []

    async def fake_set(**kwargs) -> accounts_client.Grant:
        written.append(kwargs)
        return accounts_client.Grant(
            role=kwargs["role"], role_updated_at="2026-10-14T06:00:00.000000Z"
        )

    monkeypatch.setattr(accounts_client, "set_service", fake_set)

    updated = await UserService(_CountingSession()).update_user(
        user_id=1,
        payload=UserUpdateRequest(role=UserRole.ADMINISTRATOR),
        current_user=_local_user(role=UserRole.DEVELOPER),
    )

    assert written and written[0]["email"] == "target@mkair.ru"
    assert written[0]["role"] == "ADMINISTRATOR"
    assert updated.role is UserRole.ADMINISTRATOR


@pytest.mark.asyncio
async def test_a_refused_role_is_not_applied_locally(monkeypatch: pytest.MonkeyPatch) -> None:
    """Someone changed the role meanwhile: the local copy stays as it was, loudly."""

    _enable_registry(monkeypatch)
    user = _local_user()
    _stub_user_repository(monkeypatch, [user])

    async def refuse(**_kwargs) -> accounts_client.Grant:
        raise HTTPException(status_code=409, detail="Роль изменена в реестре.")

    monkeypatch.setattr(accounts_client, "set_service", refuse)

    with pytest.raises(HTTPException) as excinfo:
        await UserService(_CountingSession()).update_user(
            user_id=1,
            payload=UserUpdateRequest(role=UserRole.ADMINISTRATOR),
            current_user=_local_user(role=UserRole.DEVELOPER),
        )

    assert excinfo.value.status_code == 409
    assert user.role is UserRole.CUSTOMER


def _as_utc(value: datetime | None) -> datetime | None:
    """A stamp as it should compare: one backend hands them back, the other keeps the offset."""

    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=UTC)


def test_the_stamp_goes_on_the_wire_with_an_offset() -> None:
    """The registry compares stamps, so the one we send must say which timezone it is in."""

    naive = datetime(2026, 10, 14, 5, 43, 35, 451482)
    aware = naive.replace(tzinfo=UTC)

    assert accounts_client._stamp_for_wire(naive) == "2026-10-14T05:43:35.451482+00:00"
    assert accounts_client._stamp_for_wire(aware) == "2026-10-14T05:43:35.451482+00:00"
    assert accounts_client._stamp_for_wire(None) is None


@pytest.mark.asyncio
async def test_user_list_remembers_the_stamp_it_took_the_role_from(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The copy remembers which registry value it mirrors — that is what a write will send."""

    _enable_registry(monkeypatch)
    user = _local_user()
    _stub_user_repository(monkeypatch, [user])

    async def fake_list() -> list[dict]:
        return _registry_listing(role="ADMINISTRATOR")

    monkeypatch.setattr(accounts_client, "list_accounts", fake_list)

    await UserService(_CountingSession()).list_users()

    assert user.role_synced_at == datetime(2026, 10, 14, 5, 43, 35, 451482, tzinfo=UTC)


@pytest.mark.asyncio
async def test_role_write_sends_the_stamp_it_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """A save says what it was looking at, so the registry can refuse a stale one."""

    _enable_registry(monkeypatch)
    stamped = datetime(2026, 10, 14, 5, 43, 35, 451482, tzinfo=UTC)
    user = _local_user(role_synced_at=stamped)
    _stub_user_repository(monkeypatch, [user])

    written: list[dict] = []

    async def fake_set(**kwargs) -> accounts_client.Grant:
        written.append(kwargs)
        return accounts_client.Grant(
            role=kwargs["role"], role_updated_at="2026-10-14T06:00:00.000000Z"
        )

    monkeypatch.setattr(accounts_client, "set_service", fake_set)

    await UserService(_CountingSession()).update_user(
        user_id=1,
        payload=UserUpdateRequest(role=UserRole.ADMINISTRATOR),
        current_user=_local_user(role=UserRole.DEVELOPER),
    )

    assert _as_utc(written[0]["if_unmodified_since"]) == stamped
    # ...and the answer's stamp becomes the new memory.
    assert user.role_synced_at == datetime(2026, 10, 14, 6, 0, 0, tzinfo=UTC)


@pytest.mark.asyncio
async def test_a_second_page_load_writes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reading twice is not two writes: matching stamps stop the mirror from rewriting rows."""

    _enable_registry(monkeypatch)
    user = _local_user(role_synced_at=datetime(2026, 10, 14, 5, 43, 35, 451482, tzinfo=UTC))
    _stub_user_repository(monkeypatch, [user])

    async def fake_list() -> list[dict]:
        return _registry_listing(role="ADMINISTRATOR")

    monkeypatch.setattr(accounts_client, "list_accounts", fake_list)

    session = _CountingSession()
    service = UserService(session)
    assert (await service.list_users())[0].role is UserRole.ADMINISTRATOR
    assert session.commits == 1
    await service.list_users()
    assert session.commits == 1
