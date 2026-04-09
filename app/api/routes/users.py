from __future__ import annotations

from fastapi import APIRouter, Response

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.schemas.user import (
    UserCreateRequest,
    UserMentionRead,
    UserRead,
    UserRoleUpdate,
    UserTemporaryPasswordResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/mentions", response_model=list[UserMentionRead])
async def list_mention_users(_: CurrentUser, db: DbSession) -> list[UserMentionRead]:
    return await UserService(db).list_mention_users()


@router.get("", response_model=list[UserRead])
async def list_users(_: AdminUser, db: DbSession) -> list[UserRead]:
    users = await UserService(db).list_users()
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, _: AdminUser, db: DbSession) -> UserRead:
    user = await UserService(db).get_user(user_id=user_id)
    return UserRead.model_validate(user)


@router.post("", response_model=UserTemporaryPasswordResponse, status_code=201)
async def create_user(
    payload: UserCreateRequest,
    current_user: AdminUser,
    db: DbSession,
) -> UserTemporaryPasswordResponse:
    user, temporary_password = await UserService(db).create_user(
        payload,
        current_user=current_user,
    )
    return UserTemporaryPasswordResponse(
        user=UserRead.model_validate(user),
        temporary_password=temporary_password,
    )


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    current_user: AdminUser,
    db: DbSession,
) -> UserRead:
    user = await UserService(db).update_user(
        user_id=user_id,
        payload=payload,
        current_user=current_user,
    )
    return UserRead.model_validate(user)


@router.patch("/{user_id}/role", response_model=UserRead)
async def update_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user: AdminUser,
    db: DbSession,
) -> UserRead:
    user = await UserService(db).update_role(
        user_id=user_id,
        role=payload.role,
        current_user=current_user,
    )
    return UserRead.model_validate(user)


@router.post("/{user_id}/reset-password", response_model=UserTemporaryPasswordResponse)
async def reset_password(
    user_id: int,
    current_user: AdminUser,
    db: DbSession,
) -> UserTemporaryPasswordResponse:
    user, temporary_password = await UserService(db).reset_password(
        user_id=user_id,
        current_user=current_user,
    )
    return UserTemporaryPasswordResponse(
        user=UserRead.model_validate(user),
        temporary_password=temporary_password,
    )


@router.delete("/{user_id}", status_code=204, response_class=Response)
async def delete_user(user_id: int, current_user: AdminUser, db: DbSession) -> Response:
    await UserService(db).delete_user(user_id=user_id, current_user=current_user)
    return Response(status_code=204)
