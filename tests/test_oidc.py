from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import settings
from app.db.models import User, UserRole
from app.services import oidc_service
from app.services.oidc_service import OidcError, OidcTransaction


def _enable_oidc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OIDC_ENABLED", True)
    monkeypatch.setattr(settings, "OIDC_CLIENT_SECRET", "client-secret")


# --------------------------------------------------------------------------- #
# pure helpers
# --------------------------------------------------------------------------- #


def test_role_from_groups_prefers_the_most_privileged() -> None:
    assert oidc_service._role_from_groups(["metrogen-developer"]) == UserRole.DEVELOPER
    assert oidc_service._role_from_groups(["metrogen-administrator"]) == UserRole.ADMINISTRATOR
    assert oidc_service._role_from_groups(["metrogen-mkair"]) == UserRole.MKAIR
    assert oidc_service._role_from_groups(["metrogen-customer"]) == UserRole.CUSTOMER
    assert oidc_service._role_from_groups(["metrogen-users"]) is None
    assert (
        oidc_service._role_from_groups(["metrogen-users", "metrogen-mkair", "metrogen-developer"])
        == UserRole.DEVELOPER
    )


def test_has_access_requires_a_metrogen_group() -> None:
    assert oidc_service._has_access(["metrogen-users"]) is True
    assert oidc_service._has_access(["metrogen-mkair"]) is True
    assert oidc_service._has_access(["authentik Admins"]) is False
    assert oidc_service._has_access([]) is False


def test_sanitize_redirect_only_allows_local_paths() -> None:
    assert oidc_service._sanitize_redirect("/generation") == "/generation"
    assert oidc_service._sanitize_redirect("//evil.example") is None
    assert oidc_service._sanitize_redirect("https://evil.example") is None
    assert oidc_service._sanitize_redirect(None) is None


def test_claim_groups_accepts_list_and_string() -> None:
    assert oidc_service._claim_groups({"groups": ["a", "b"]}) == ["a", "b"]
    assert oidc_service._claim_groups({"groups": "a, b"}) == ["a", "b"]
    assert oidc_service._claim_groups({}) == []


@pytest.mark.asyncio
async def test_build_login_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_oidc(monkeypatch)

    async def _fake_discovery() -> oidc_service._Discovery:
        return oidc_service._Discovery(
            authorization_endpoint="https://auth.example/authorize",
            token_endpoint="https://auth.example/token",
            jwks_uri="https://auth.example/jwks",
            fetched_at=0.0,
        )

    monkeypatch.setattr(oidc_service, "_get_discovery", _fake_discovery)

    url, transaction = await oidc_service.build_login_url(redirect="/generation")

    assert url.startswith("https://auth.example/authorize?")
    assert "code_challenge_method=S256" in url
    assert f"client_id={settings.OIDC_CLIENT_ID}" in url
    assert transaction["state"] and transaction["nonce"] and transaction["code_verifier"]
    assert transaction["redirect"] == "/generation"


@pytest.mark.asyncio
async def test_build_login_url_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "OIDC_ENABLED", False)
    with pytest.raises(OidcError):
        await oidc_service.build_login_url(redirect=None)


# --------------------------------------------------------------------------- #
# id token verification
# --------------------------------------------------------------------------- #


def _rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _stub_jwks(monkeypatch: pytest.MonkeyPatch, key) -> None:
    public_key = key.public_key()

    class _StubKey:
        key = public_key

    class _StubClient:
        uri = "https://auth.example/jwks"

        def get_signing_key_from_jwt(self, _token: str) -> _StubKey:
            return _StubKey()

    monkeypatch.setattr(oidc_service, "_get_jwks_client", lambda _uri: _StubClient())

    async def _fake_discovery() -> oidc_service._Discovery:
        return oidc_service._Discovery("a", "t", "https://auth.example/jwks", 0.0)

    monkeypatch.setattr(oidc_service, "_get_discovery", _fake_discovery)


@pytest.mark.asyncio
async def test_verify_id_token_accepts_valid_and_rejects_wrong_nonce(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key = _rsa_key()
    now = datetime.now(tz=UTC)
    token = jwt.encode(
        {
            "sub": "hashed-1",
            "aud": settings.OIDC_CLIENT_ID,
            "iss": settings.OIDC_ISSUER,
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "nonce": "nonce-123",
            "email": "user@mkair.ru",
        },
        key,
        algorithm="RS256",
    )
    _stub_jwks(monkeypatch, key)

    claims = await oidc_service._verify_id_token(token, nonce="nonce-123")
    assert claims["email"] == "user@mkair.ru"

    with pytest.raises(OidcError):
        await oidc_service._verify_id_token(token, nonce="other")


@pytest.mark.asyncio
async def test_verify_id_token_rejects_wrong_issuer(monkeypatch: pytest.MonkeyPatch) -> None:
    key = _rsa_key()
    now = datetime.now(tz=UTC)
    token = jwt.encode(
        {
            "sub": "1",
            "aud": settings.OIDC_CLIENT_ID,
            "iss": "https://evil.example/",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "nonce": "n",
        },
        key,
        algorithm="RS256",
    )
    _stub_jwks(monkeypatch, key)
    with pytest.raises(OidcError):
        await oidc_service._verify_id_token(token, nonce="n")


# --------------------------------------------------------------------------- #
# resolve_callback
# --------------------------------------------------------------------------- #


class _DummySession:
    async def commit(self) -> None:
        return None

    async def refresh(self, _user: object) -> None:
        return None


def _patch_callback(
    monkeypatch: pytest.MonkeyPatch, *, claims: dict, existing: User | None
) -> None:
    async def _fake_exchange(**_kw) -> dict:
        return {"id_token": "token"}

    async def _fake_verify(_token: str, nonce: str) -> dict:
        return claims

    class _StubUsers:
        def __init__(self, _session: object) -> None:
            pass

        async def get_by_email(self, _email: str) -> User | None:
            return existing

        async def add(self, user: User) -> User:
            return user

    monkeypatch.setattr(oidc_service, "_exchange_code", _fake_exchange)
    monkeypatch.setattr(oidc_service, "_verify_id_token", _fake_verify)
    monkeypatch.setattr(oidc_service, "UserRepository", _StubUsers)


@pytest.mark.asyncio
async def test_resolve_callback_links_user_and_maps_role(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_oidc(monkeypatch)
    existing = User(
        id=1,
        first_name="Иван",
        last_name="Тестов",
        email="user@mkair.ru",
        password_hash="!",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    _patch_callback(
        monkeypatch,
        claims={"email": "user@mkair.ru", "groups": ["metrogen-users", "metrogen-mkair"]},
        existing=existing,
    )

    transaction = OidcTransaction(state="s", nonce="n", code_verifier="v", redirect="/generation")
    user, redirect = await oidc_service.resolve_callback(
        session=_DummySession(),
        code="code",
        state="s",
        transaction=transaction,
    )

    assert user.role == UserRole.MKAIR
    assert user.last_login_at is not None
    assert redirect == "/generation"


@pytest.mark.asyncio
async def test_resolve_callback_rejects_bad_state(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable_oidc(monkeypatch)
    transaction = OidcTransaction(state="s", nonce="n", code_verifier="v", redirect=None)
    with pytest.raises(OidcError):
        await oidc_service.resolve_callback(
            session=_DummySession(),
            code="code",
            state="tampered",
            transaction=transaction,
        )


@pytest.mark.asyncio
async def test_resolve_callback_rejects_user_without_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_oidc(monkeypatch)
    _patch_callback(
        monkeypatch,
        claims={"email": "user@mkair.ru", "groups": ["other-team"]},
        existing=None,
    )
    transaction = OidcTransaction(state="s", nonce="n", code_verifier="v", redirect=None)
    with pytest.raises(OidcError):
        await oidc_service.resolve_callback(
            session=_DummySession(),
            code="code",
            state="s",
            transaction=transaction,
        )


# --------------------------------------------------------------------------- #
# HTTP surface
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_oidc_status_is_disabled_by_default(async_client) -> None:
    response = await async_client.get("/api/v1/auth/oidc/status")
    assert response.status_code == 200
    assert response.json() == {"enabled": False}


@pytest.mark.asyncio
async def test_oidc_login_redirects_to_error_when_disabled(async_client) -> None:
    response = await async_client.get("/api/v1/auth/oidc/login", follow_redirects=False)
    assert response.status_code == 302
    assert "#oidc_error=disabled" in response.headers["location"]
