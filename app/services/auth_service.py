from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import User, UserRole
from app.db.repositories import UserRepository
from app.schemas.auth import ChangePasswordRequest, LoginRequest
from app.schemas.user import UserProfileUpdateRequest
from app.services.notification_service import NotificationService
from app.utils.password_policy import validate_password_policy
from app.utils.security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.notifications = NotificationService()

    async def login(self, payload: LoginRequest) -> tuple[User, str]:
        email = _normalize_email(payload.email)
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        now = datetime.now(tz=UTC)
        user.last_login_at = now
        user.last_seen_at = now
        await self.session.commit()
        await self.session.refresh(user)
        return user, self._create_access_token_for_user(user)

    async def change_password(self, *, user: User, payload: ChangePasswordRequest) -> None:
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        if payload.new_password != payload.confirm_new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password confirmation does not match.",
            )
        if payload.current_password == payload.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the current password.",
            )

        validate_password_policy(payload.new_password)
        user.password_hash = hash_password(payload.new_password)
        user.must_change_password = False
        user.password_changed_at = datetime.now(tz=UTC)
        await self.session.commit()
        await self.session.refresh(user)

    async def update_profile(self, *, user: User, payload: UserProfileUpdateRequest) -> User:
        if "phone" in payload.model_fields_set:
            user.phone = _normalize_optional_text(payload.phone, limit=64)
        if "organization" in payload.model_fields_set:
            user.organization = _normalize_optional_text(payload.organization, limit=255)
        if "position" in payload.model_fields_set:
            user.position = _normalize_optional_text(payload.position, limit=255)
        if "facility" in payload.model_fields_set:
            user.facility = _normalize_optional_text(payload.facility, limit=255)
        if "mention_email_notifications_enabled" in payload.model_fields_set:
            user.mention_email_notifications_enabled = bool(
                payload.mention_email_notifications_enabled
            )
        if "theme_preference" in payload.model_fields_set:
            user.theme_preference = payload.theme_preference
        if "enabled_theme_options" in payload.model_fields_set:
            options = payload.enabled_theme_options or []
            if not options:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Хотя бы одна тема должна оставаться доступной.",
                )
            user.enabled_theme_options = [str(option.value) for option in options]

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def send_test_mention_email(self, *, user: User) -> None:
        self.notifications.send_test_email(
            recipient_email=user.email,
            recipient_name=" ".join(
                part for part in [user.first_name, user.last_name] if part and part.strip()
            ).strip()
            or user.email,
        )

    def _create_access_token_for_user(self, user: User) -> str:
        return create_access_token(
            user_id=user.id,
            role=_normalize_role(user.role),
            secret_key=settings.SECRET_KEY,
            ttl_hours=settings.ACCESS_TOKEN_TTL_HOURS,
        )


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not normalized or "@" not in normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email must be valid.",
        )
    return normalized


def _normalize_optional_text(value: str | None, *, limit: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > limit:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Field is too long. Maximum length is {limit} characters.",
        )
    return normalized


def _normalize_role(role: UserRole | str) -> str:
    return role.value if isinstance(role, UserRole) else str(role)
