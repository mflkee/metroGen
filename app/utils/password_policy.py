from __future__ import annotations

from fastapi import HTTPException, status

PASSWORD_POLICY_MESSAGE = (
    "Пароль должен быть не короче 6 символов и содержать хотя бы одну букву и одну цифру."
)


def validate_password_policy(password: str) -> None:
    if (
        len(password) < 6
        or not any(character.isalpha() for character in password)
        or not any(character.isdigit() for character in password)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=PASSWORD_POLICY_MESSAGE,
        )
