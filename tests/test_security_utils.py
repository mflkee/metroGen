from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_roundtrip():
    password = "MetroGen123"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_access_token_roundtrip():
    token = create_access_token(
        user_id=17,
        role="ADMINISTRATOR",
        secret_key="test-secret",
        ttl_hours=1,
    )

    payload = decode_access_token(token, "test-secret")

    assert payload["sub"] == 17
    assert payload["role"] == "ADMINISTRATOR"
