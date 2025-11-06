from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.repositories.core import OwnerRepository
from app.schemas.owner import OwnerCreate, OwnerOut, OwnerUpdate

router = APIRouter(prefix="/api/v1/owners", tags=["owners"])


@router.post(
    "",
    response_model=OwnerOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update owner by name",
)
async def create_owner(payload: OwnerCreate, session: AsyncSession = Depends(get_db)) -> OwnerOut:
    repo = OwnerRepository(session)
    owner = await repo.upsert_owner(
        name=payload.name,
        inn=payload.inn,
        aliases=payload.aliases or [],
    )
    await session.commit()
    await session.refresh(owner)
    return OwnerOut.from_model(owner)


@router.patch(
    "/{owner_id}",
    response_model=OwnerOut,
    summary="Update owner fields",
)
async def update_owner(
    owner_id: int,
    payload: OwnerUpdate,
    session: AsyncSession = Depends(get_db),
) -> OwnerOut:
    repo = OwnerRepository(session)
    owner = await repo.get_by_id(owner_id)
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="owner not found")

    if payload.name is not None:
        owner.name = payload.name
    if payload.inn is not None:
        owner.inn = payload.inn

    aliases = payload.aliases or []
    if aliases:
        await repo.ensure_aliases(owner, aliases)

    await session.commit()
    await session.refresh(owner)
    return OwnerOut.from_model(owner)
