from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import and_, delete, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db import models
from app.db.models import MethodologyPointType
from app.db.repositories.utils import (
    normalize_methodology_alias,
    normalize_owner_alias,
)
from app.utils.normalization import normalize_serial

__all__ = (
    "BaseRepository",
    "OwnerRepository",
    "MethodologyRepository",
    "RegistryRepository",
    "InstrumentRepository",
    "EtalonRepository",
    "AuxiliaryInstrumentRepository",
    "UserRepository",
    "MethodologyPointPayload",
)


class BaseRepository:
    """Shared helper functionality for repository classes."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, instance: models.Base, *, flush: bool = True) -> Any:
        self.session.add(instance)
        if flush:
            await self.session.flush()
        return instance

    async def delete(self, instance: models.Base, *, flush: bool = True) -> None:
        await self.session.delete(instance)
        if flush:
            await self.session.flush()


class OwnerRepository(BaseRepository):
    async def get_by_id(self, owner_id: int) -> models.Owner | None:
        stmt = select(models.Owner).where(models.Owner.id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> models.Owner | None:
        if not name:
            return None
        stmt = select(models.Owner).where(models.Owner.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_inn(self, inn: str | None) -> models.Owner | None:
        if not inn:
            return None
        stmt = select(models.Owner).where(models.Owner.inn == inn)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_alias(self, alias: str) -> models.Owner | None:
        normalized = normalize_owner_alias(alias)
        if not normalized:
            return None
        stmt = (
            select(models.Owner)
            .join(models.OwnerAlias)
            .options(joinedload(models.Owner.aliases))
            .where(models.OwnerAlias.normalized_alias == normalized)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def upsert_owner(
        self,
        *,
        name: str,
        inn: str | None = None,
        aliases: Sequence[str] | None = None,
    ) -> models.Owner:
        owner = await self.get_by_name(name)
        if owner is None:
            owner = models.Owner(name=name, inn=inn)
            await self.add(owner)
        else:
            if inn and owner.inn != inn:
                owner.inn = inn

        if aliases:
            await self.ensure_aliases(owner, aliases)
        return owner

    async def ensure_aliases(
        self, owner: models.Owner, aliases: Iterable[str]
    ) -> list[models.OwnerAlias]:
        ensured: list[models.OwnerAlias] = []
        for alias in aliases:
            normalized = normalize_owner_alias(alias)
            if not normalized:
                continue
            existing = await self._fetch_alias(normalized)
            if existing is not None:
                ensured.append(existing)
                continue

            alias_row = models.OwnerAlias(
                owner_id=owner.id,
                alias=alias,
                normalized_alias=normalized,
            )
            await self.add(alias_row)
            ensured.append(alias_row)

        return ensured

    async def _fetch_alias(self, normalized_alias: str) -> models.OwnerAlias | None:
        stmt = select(models.OwnerAlias).where(
            models.OwnerAlias.normalized_alias == normalized_alias
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


@dataclass(slots=True)
class MethodologyPointPayload:
    position: int
    label: str
    point_type: MethodologyPointType = MethodologyPointType.BOOL
    default_text: str | None = None


class MethodologyRepository(BaseRepository):
    async def get_by_code(self, code: str) -> models.Methodology | None:
        stmt = (
            select(models.Methodology)
            .options(
                selectinload(models.Methodology.points), selectinload(models.Methodology.aliases)
            )
            .where(models.Methodology.code == code)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_alias(self, alias: str) -> models.Methodology | None:
        normalized = normalize_methodology_alias(alias)
        if not normalized:
            return None
        stmt = (
            select(models.Methodology)
            .join(models.MethodologyAlias)
            .options(
                joinedload(models.Methodology.aliases),
                selectinload(models.Methodology.points),
            )
            .where(models.MethodologyAlias.normalized_alias == normalized)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def upsert_methodology(
        self,
        *,
        code: str,
        title: str,
        document: str | None = None,
        notes: str | None = None,
        allowable_variation_pct: float | None = None,
    ) -> models.Methodology:
        methodology = await self.get_by_code(code)
        if methodology is None:
            methodology = models.Methodology(
                code=code,
                title=title,
                document=document,
                notes=notes,
                allowable_variation_pct=allowable_variation_pct,
            )
            await self.add(methodology)
            return methodology

        methodology.title = title
        methodology.document = document
        methodology.notes = notes
        methodology.allowable_variation_pct = allowable_variation_pct
        return methodology

    async def ensure_aliases(
        self,
        methodology: models.Methodology,
        aliases: Iterable[tuple[str, int] | str],
    ) -> list[models.MethodologyAlias]:
        ensured: list[models.MethodologyAlias] = []
        for alias_item in aliases:
            if isinstance(alias_item, tuple):
                alias, weight = alias_item
            else:
                alias, weight = alias_item, 100

            normalized = normalize_methodology_alias(alias)
            if not normalized:
                continue

            existing = await self._fetch_alias(normalized)
            if existing is not None:
                if existing.methodology_id == methodology.id and weight != existing.weight:
                    existing.weight = weight
                ensured.append(existing)
                continue

            alias_row = models.MethodologyAlias(
                methodology_id=methodology.id,
                alias=alias,
                normalized_alias=normalized,
                weight=weight,
            )
            await self.add(alias_row)
            ensured.append(alias_row)

        return ensured

    async def replace_points(
        self,
        methodology: models.Methodology,
        points: Sequence[MethodologyPointPayload],
    ) -> None:
        await self.session.execute(
            delete(models.MethodologyPoint).where(
                models.MethodologyPoint.methodology_id == methodology.id
            )
        )

        ordered = sorted(points, key=lambda item: item.position)
        for payload in ordered:
            point_type = (
                payload.point_type.value
                if isinstance(payload.point_type, MethodologyPointType)
                else payload.point_type
            )
            if isinstance(point_type, str):
                try:
                    point_type = MethodologyPointType(point_type.lower())
                except ValueError:
                    point_type = MethodologyPointType.BOOL
            elif not isinstance(point_type, MethodologyPointType):
                point_type = MethodologyPointType.BOOL

            point_type_value = (
                point_type.value
                if isinstance(point_type, MethodologyPointType)
                else str(point_type).lower()
            )
            point = models.MethodologyPoint(
                methodology_id=methodology.id,
                position=payload.position,
                label=payload.label,
                point_type=point_type_value,
                default_text=payload.default_text,
            )
            self.session.add(point)
        await self.session.flush()

    async def _fetch_alias(self, normalized_alias: str) -> models.MethodologyAlias | None:
        stmt = select(models.MethodologyAlias).where(
            models.MethodologyAlias.normalized_alias == normalized_alias
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class RegistryRepository(BaseRepository):
    async def upsert_entry(
        self,
        *,
        source_file: str,
        row_index: int,
        values: dict[str, Any],
    ) -> models.VerificationRegistryEntry:
        stmt = select(models.VerificationRegistryEntry).where(
            models.VerificationRegistryEntry.source_file == source_file,
            models.VerificationRegistryEntry.row_index == row_index,
        )
        result = await self.session.execute(stmt)
        entry = result.scalar_one_or_none()

        if entry is None:
            entry = models.VerificationRegistryEntry(
                source_file=source_file,
                row_index=row_index,
                **values,
            )
            await self.add(entry)
        else:
            for key, value in values.items():
                setattr(entry, key, value)

        return entry

    async def deactivate_for_source(self, source_file: str) -> int:
        stmt = select(models.VerificationRegistryEntry).where(
            models.VerificationRegistryEntry.source_file == source_file,
            models.VerificationRegistryEntry.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        entries = result.scalars().all()
        for entry in entries:
            entry.is_active = False
        if entries:
            await self.session.flush()
        return len(entries)

    async def find_active_by_serial(
        self, normalized_serial: str
    ) -> list[models.VerificationRegistryEntry]:
        stmt = select(models.VerificationRegistryEntry).where(
            models.VerificationRegistryEntry.normalized_serial == normalized_serial,
            models.VerificationRegistryEntry.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_active_by_serials(
        self, normalized_serials: Iterable[str]
    ) -> dict[str, list[models.VerificationRegistryEntry]]:
        serial_list = [normalize_serial(value) for value in normalized_serials]
        filtered = [serial for serial in {s for s in serial_list if s}]
        if not filtered:
            return {}

        stmt = select(models.VerificationRegistryEntry).where(
            models.VerificationRegistryEntry.normalized_serial.in_(filtered),
            models.VerificationRegistryEntry.is_active.is_(True),
        )
        result = await self.session.execute(stmt)

        mapping: dict[str, list[models.VerificationRegistryEntry]] = {
            serial: [] for serial in filtered
        }
        for entry in result.scalars():
            if entry.normalized_serial:
                mapping.setdefault(entry.normalized_serial, []).append(entry)
        return mapping


class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: int) -> models.User | None:
        stmt = select(models.User).where(models.User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, user_id: int) -> models.User | None:
        stmt = select(models.User).where(models.User.id == user_id).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_for_update(self, email: str) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[models.User]:
        stmt = select(models.User).order_by(models.User.last_name, models.User.first_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_active(self) -> list[models.User]:
        stmt = (
            select(models.User)
            .where(models.User.is_active.is_(True))
            .order_by(models.User.last_name, models.User.first_name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

class InstrumentRepository(BaseRepository):
    async def find_by_serial(self, normalized_serial: str) -> list[models.MeasuringInstrument]:
        stmt = select(models.MeasuringInstrument).where(
            models.MeasuringInstrument.normalized_serial == normalized_serial
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_instrument(
        self,
        *,
        normalized_serial: str,
        certificate_no: str | None,
        values: dict[str, Any],
    ) -> models.MeasuringInstrument:
        stmt = select(models.MeasuringInstrument).where(
            models.MeasuringInstrument.normalized_serial == normalized_serial,
            models.MeasuringInstrument.certificate_no == certificate_no,
        )
        result = await self.session.execute(stmt)
        instrument = result.scalar_one_or_none()

        if instrument is None:
            instrument = models.MeasuringInstrument(
                normalized_serial=normalized_serial,
                certificate_no=certificate_no,
                **values,
            )
            await self.add(instrument)
        else:
            for key, value in values.items():
                setattr(instrument, key, value)

        return instrument


class EtalonRepository(BaseRepository):
    async def get_device(
        self, reg_number: str, manufacture_num: str | None
    ) -> models.EtalonDevice | None:
        stmt = select(models.EtalonDevice).where(
            models.EtalonDevice.reg_number == reg_number,
            models.EtalonDevice.manufacture_num == manufacture_num,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_device(
        self,
        *,
        reg_number: str,
        manufacture_num: str | None,
        values: dict[str, Any],
    ) -> models.EtalonDevice:
        device = await self.get_device(reg_number, manufacture_num)
        if device is None:
            device = models.EtalonDevice(
                reg_number=reg_number,
                manufacture_num=manufacture_num,
                **values,
            )
            await self.add(device)
        else:
            for key, value in values.items():
                setattr(device, key, value)
        return device

    async def upsert_certification(
        self,
        *,
        device: models.EtalonDevice,
        certificate_no: str,
        values: dict[str, Any],
    ) -> models.EtalonCertification:
        stmt = select(models.EtalonCertification).where(
            models.EtalonCertification.etalon_device_id == device.id,
            models.EtalonCertification.certificate_no == certificate_no,
        )
        result = await self.session.execute(stmt)
        certification = result.scalar_one_or_none()

        if certification is None:
            certification = models.EtalonCertification(
                etalon_device_id=device.id,
                certificate_no=certificate_no,
                **values,
            )
            await self.add(certification)
        else:
            for key, value in values.items():
                setattr(certification, key, value)

        return certification


class AuxiliaryInstrumentRepository(BaseRepository):
    async def upsert_instrument(
        self,
        *,
        reg_number: str,
        manufacture_num: str,
        values: dict[str, Any],
    ) -> models.AuxiliaryVerificationInstrument:
        normalized = normalize_serial(manufacture_num)
        stmt = select(models.AuxiliaryVerificationInstrument).where(
            models.AuxiliaryVerificationInstrument.reg_number == reg_number,
            models.AuxiliaryVerificationInstrument.normalized_serial == normalized,
        )
        result = await self.session.execute(stmt)
        instrument = result.scalar_one_or_none()

        if instrument is None:
            instrument = models.AuxiliaryVerificationInstrument(
                reg_number=reg_number,
                normalized_serial=normalized,
                manufacture_num=manufacture_num,
                **values,
            )
            await self.add(instrument)
        else:
            instrument.manufacture_num = manufacture_num
            for key, value in values.items():
                setattr(instrument, key, value)

        return instrument

    async def list_all(self) -> list[models.AuxiliaryVerificationInstrument]:
        stmt = (
            select(models.AuxiliaryVerificationInstrument)
            .order_by(
                models.AuxiliaryVerificationInstrument.reg_number.asc(),
                models.AuxiliaryVerificationInstrument.normalized_serial.asc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_pairs(
        self, pairs: Sequence[tuple[str, str]]
    ) -> dict[tuple[str, str], models.AuxiliaryVerificationInstrument]:
        normalized_pairs = [
            (str(reg).strip(), normalize_serial(serial))
            for reg, serial in pairs
            if str(reg).strip() and normalize_serial(serial)
        ]
        if not normalized_pairs:
            return {}

        clauses = [
            and_(
                models.AuxiliaryVerificationInstrument.reg_number == reg,
                models.AuxiliaryVerificationInstrument.normalized_serial == serial,
            )
            for reg, serial in normalized_pairs
        ]
        stmt = select(models.AuxiliaryVerificationInstrument).where(or_(*clauses))
        result = await self.session.execute(stmt)
        instruments = list(result.scalars().all())
        return {
            (instrument.reg_number, instrument.normalized_serial): instrument
            for instrument in instruments
            if instrument.reg_number and instrument.normalized_serial
        }

    async def prune_to_pairs(self, pairs: Sequence[tuple[str, str]]) -> int:
        normalized_pairs = [
            (str(reg).strip(), normalize_serial(serial))
            for reg, serial in pairs
            if str(reg).strip() and normalize_serial(serial)
        ]
        if not normalized_pairs:
            stmt = delete(models.AuxiliaryVerificationInstrument)
            result = await self.session.execute(stmt)
            return max(int(result.rowcount or 0), 0)

        keep_clauses = [
            and_(
                models.AuxiliaryVerificationInstrument.reg_number == reg,
                models.AuxiliaryVerificationInstrument.normalized_serial == serial,
            )
            for reg, serial in normalized_pairs
        ]
        stmt = delete(models.AuxiliaryVerificationInstrument).where(not_(or_(*keep_clauses)))
        result = await self.session.execute(stmt)
        return max(int(result.rowcount or 0), 0)
