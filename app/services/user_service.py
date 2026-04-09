from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import User, UserRole
from app.db.repositories import UserRepository
from app.schemas.user import UserCreateRequest, UserMentionRead, UserUpdateRequest
from app.services.notification_service import NotificationService
from app.utils.password_policy import validate_password_policy
from app.utils.security import create_temporary_password, hash_password


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.notifications = NotificationService()

    async def ensure_bootstrap_admin(self) -> User | None:
        email = _normalize_email(settings.BOOTSTRAP_ADMIN_EMAIL)
        password = settings.BOOTSTRAP_ADMIN_PASSWORD.strip()
        validate_password_policy(password)

        user = await self.users.get_by_email_for_update(email)
        if user is not None:
            if user.role not in {UserRole.DEVELOPER, UserRole.ADMINISTRATOR}:
                user.role = UserRole.ADMINISTRATOR
            if not user.is_active:
                user.is_active = True
            await self.session.commit()
            await self.session.refresh(user)
            return user

        user = User(
            first_name=_normalize_required_name(
                settings.BOOTSTRAP_ADMIN_FIRST_NAME,
                field_label="First name",
            ),
            last_name=_normalize_required_name(
                settings.BOOTSTRAP_ADMIN_LAST_NAME,
                field_label="Last name",
            ),
            patronymic=_normalize_optional_name(settings.BOOTSTRAP_ADMIN_PATRONYMIC),
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMINISTRATOR,
            is_active=True,
            must_change_password=True,
        )
        await self.users.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def list_users(self) -> list[User]:
        return await self.users.list_all()

    async def list_mention_users(self) -> list[UserMentionRead]:
        users = await self.users.list_active()
        return build_user_mention_reads(users)

    async def get_user(self, *, user_id: int) -> User:
        user = await self.users.get_by_id(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    async def create_user(
        self,
        payload: UserCreateRequest,
        *,
        current_user: User,
    ) -> tuple[User, str]:
        self._assert_user_management_target_access(
            current_user=current_user,
            target_user=None,
            next_role=payload.role,
        )
        email = _normalize_email(payload.email)
        if await self.users.get_by_email(email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        temporary_password = (
            payload.temporary_password.strip()
            if payload.temporary_password and payload.temporary_password.strip()
            else create_temporary_password()
        )
        validate_password_policy(temporary_password)

        user = User(
            first_name=_normalize_required_name(payload.first_name, field_label="First name"),
            last_name=_normalize_required_name(payload.last_name, field_label="Last name"),
            patronymic=_normalize_optional_name(payload.patronymic),
            email=email,
            password_hash=hash_password(temporary_password),
            role=payload.role,
            is_active=bool(payload.is_active),
            must_change_password=True,
        )
        await self.users.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        if self.notifications.is_configured():
            self.notifications.send_temporary_password_email(
                recipient_email=user.email,
                recipient_name=_format_user_display_name(user),
                temporary_password=temporary_password,
            )

        return user, temporary_password

    async def update_user(
        self,
        *,
        user_id: int,
        payload: UserUpdateRequest,
        current_user: User,
    ) -> User:
        user = await self.users.get_by_id_for_update(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        next_role = payload.role or user.role
        self._assert_user_management_target_access(
            current_user=current_user,
            target_user=user,
            next_role=next_role,
        )

        if payload.first_name is not None:
            user.first_name = _normalize_required_name(payload.first_name, field_label="First name")
        if payload.last_name is not None:
            user.last_name = _normalize_required_name(payload.last_name, field_label="Last name")
        if payload.patronymic is not None:
            user.patronymic = _normalize_optional_name(payload.patronymic)
        if payload.role is not None:
            user.role = payload.role
        if payload.is_active is not None:
            user.is_active = bool(payload.is_active)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_role(self, *, user_id: int, role: UserRole, current_user: User) -> User:
        return await self.update_user(
            user_id=user_id,
            payload=UserUpdateRequest(role=role),
            current_user=current_user,
        )

    async def reset_password(self, *, user_id: int, current_user: User) -> tuple[User, str]:
        user = await self.users.get_by_id_for_update(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        self._assert_user_management_target_access(
            current_user=current_user,
            target_user=user,
            next_role=user.role,
        )

        temporary_password = create_temporary_password()
        user.password_hash = hash_password(temporary_password)
        user.must_change_password = True
        user.password_changed_at = None
        await self.session.commit()
        await self.session.refresh(user)

        if self.notifications.is_configured():
            self.notifications.send_temporary_password_email(
                recipient_email=user.email,
                recipient_name=_format_user_display_name(user),
                temporary_password=temporary_password,
            )

        return user, temporary_password

    async def delete_user(self, *, user_id: int, current_user: User) -> None:
        user = await self.users.get_by_id_for_update(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить текущего пользователя.",
            )

        self._assert_user_management_target_access(
            current_user=current_user,
            target_user=user,
            next_role=user.role,
        )
        await self.users.delete(user)
        await self.session.commit()

    def _assert_user_management_target_access(
        self,
        *,
        current_user: User,
        target_user: User | None,
        next_role: UserRole,
    ) -> None:
        if current_user.role == UserRole.DEVELOPER:
            return

        if current_user.role != UserRole.ADMINISTRATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator access is required.",
            )

        if next_role == UserRole.DEVELOPER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only developers can manage developer accounts.",
            )

        if target_user is not None and target_user.role == UserRole.DEVELOPER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only developers can manage developer accounts.",
            )


def has_admin_access(role: UserRole | str | None) -> bool:
    return role in {UserRole.DEVELOPER, UserRole.ADMINISTRATOR, "DEVELOPER", "ADMINISTRATOR"}


def has_operator_access(role: UserRole | str | None) -> bool:
    return has_admin_access(role) or role in {UserRole.MKAIR, "MKAIR"}


def build_user_mention_reads(users: list[User]) -> list[UserMentionRead]:
    return [
        UserMentionRead(
            id=user.id,
            display_name=_format_user_display_name(user),
            email=user.email,
            mention_key=f"@{user.email.split('@', 1)[0]}",
        )
        for user in users
    ]


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not normalized or "@" not in normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email must be valid.",
        )
    return normalized


def _normalize_required_name(value: str, *, field_label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_label} is required.",
        )
    return normalized[:255]


def _normalize_optional_name(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized[:255] if normalized else None


def _format_user_display_name(user: User) -> str:
    return " ".join(
        part for part in [user.last_name, user.first_name, user.patronymic] if part and part.strip()
    )
