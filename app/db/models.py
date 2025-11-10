from __future__ import annotations

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import JSONBType


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    supported_fields: Mapped[dict[str, Any] | list[str] | None] = mapped_column(
        JSONBType(), nullable=True
    )

    protocols: Mapped[list[Protocol]] = relationship(back_populates="template")


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    inn: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    protocols: Mapped[list[Protocol]] = relationship(back_populates="owner")
    aliases: Mapped[list[OwnerAlias]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    instruments: Mapped[list[MeasuringInstrument]] = relationship(back_populates="owner")


class OwnerAlias(Base):
    __tablename__ = "owner_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    owner: Mapped[Owner] = relationship(back_populates="aliases")


class VerificationRegistryEntry(Base):
    __tablename__ = "verification_registry_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_file: Mapped[str] = mapped_column(String(512), nullable=False)
    source_sheet: Mapped[str | None] = mapped_column(String(255), nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    normalized_serial: Mapped[str | None] = mapped_column(String(128), index=True)
    document_no: Mapped[str | None] = mapped_column(String(128), index=True)
    protocol_no: Mapped[str | None] = mapped_column(String(128), index=True)
    owner_name_raw: Mapped[str | None] = mapped_column(String(255))
    methodology_raw: Mapped[str | None] = mapped_column(String(255))
    instrument_kind: Mapped[str | None] = mapped_column(String(64), index=True)
    verification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONBType(), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    instruments: Mapped[list[MeasuringInstrument]] = relationship(back_populates="registry_entry")
    protocols: Mapped[list[Protocol]] = relationship(back_populates="registry_entry")


class Methodology(Base):
    __tablename__ = "methodologies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    allowable_variation_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    aliases: Mapped[list[MethodologyAlias]] = relationship(
        back_populates="methodology", cascade="all, delete-orphan"
    )
    points: Mapped[list[MethodologyPoint]] = relationship(
        back_populates="methodology", cascade="all, delete-orphan"
    )
    instruments: Mapped[list[MeasuringInstrument]] = relationship(back_populates="methodology")


class MethodologyAlias(Base):
    __tablename__ = "methodology_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    methodology_id: Mapped[int] = mapped_column(ForeignKey("methodologies.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    weight: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default=text("100")
    )

    methodology: Mapped[Methodology] = relationship(back_populates="aliases")


class MethodologyPointType(str, PyEnum):
    BOOL = "bool"
    CLAUSE = "clause"
    CUSTOM = "custom"


class MethodologyPoint(Base):
    __tablename__ = "methodology_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    methodology_id: Mapped[int] = mapped_column(ForeignKey("methodologies.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(512), nullable=False)
    point_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=MethodologyPointType.BOOL.value,
        server_default=text("'bool'"),
    )
    default_text: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    methodology: Mapped[Methodology] = relationship(back_populates="points")


class EtalonDevice(Base):
    __tablename__ = "etalon_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reg_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    mitype_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacture_num: Mapped[str | None] = mapped_column(String(128), nullable=True)
    manufacture_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rank_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    schema_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONBType(), nullable=True)

    certifications: Mapped[list[EtalonCertification]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )


class EtalonCertification(Base):
    __tablename__ = "etalon_certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    etalon_device_id: Mapped[int] = mapped_column(
        ForeignKey("etalon_devices.id", ondelete="CASCADE")
    )
    certificate_no: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    verification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    source: Mapped[str] = mapped_column(
        String(64), nullable=False, default="arshin", server_default=text("'arshin'")
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONBType(), nullable=True)

    device: Mapped[EtalonDevice] = relationship(back_populates="certifications")
    protocols: Mapped[list[Protocol]] = relationship(back_populates="etalon_certification")


class MeasuringInstrument(Base):
    __tablename__ = "measuring_instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    normalized_serial: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    designation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacture_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("owners.id", ondelete="SET NULL"), nullable=True
    )
    methodology_id: Mapped[int | None] = mapped_column(
        ForeignKey("methodologies.id", ondelete="SET NULL"), nullable=True
    )
    registry_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("verification_registry_entries.id", ondelete="SET NULL"), nullable=True
    )
    certificate_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    certificate_valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    vri_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONBType(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("now()"),
        server_onupdate=text("now()"),
    )

    owner: Mapped[Owner | None] = relationship(back_populates="instruments")
    methodology: Mapped[Methodology | None] = relationship(back_populates="instruments")
    registry_entry: Mapped[VerificationRegistryEntry | None] = relationship(
        back_populates="instruments"
    )
    protocols: Mapped[list[Protocol]] = relationship(back_populates="measuring_instrument")


class Etalon(Base):
    __tablename__ = "etalons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reg_number: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certificate: Mapped[str | None] = mapped_column(String(128), nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    protocols: Mapped[list[Protocol]] = relationship(back_populates="etalon")


class Protocol(Base):
    __tablename__ = "protocols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    methodology: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vri_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("owners.id"))
    template_id: Mapped[int | None] = mapped_column(ForeignKey("templates.id"))
    etalon_id: Mapped[int | None] = mapped_column(ForeignKey("etalons.id"))
    registry_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("verification_registry_entries.id", ondelete="SET NULL"), nullable=True
    )
    measuring_instrument_id: Mapped[int | None] = mapped_column(
        ForeignKey("measuring_instruments.id", ondelete="SET NULL"), nullable=True
    )
    etalon_certification_id: Mapped[int | None] = mapped_column(
        ForeignKey("etalon_certifications.id", ondelete="SET NULL"), nullable=True
    )

    context: Mapped[dict[str, Any] | None] = mapped_column(JSONBType(), nullable=True)

    owner: Mapped[Owner | None] = relationship(back_populates="protocols")
    template: Mapped[Template | None] = relationship(back_populates="protocols")
    etalon: Mapped[Etalon | None] = relationship(back_populates="protocols")
    registry_entry: Mapped[VerificationRegistryEntry | None] = relationship(
        back_populates="protocols"
    )
    measuring_instrument: Mapped[MeasuringInstrument | None] = relationship(
        back_populates="protocols"
    )
    etalon_certification: Mapped[EtalonCertification | None] = relationship(
        back_populates="protocols"
    )
