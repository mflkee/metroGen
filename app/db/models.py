from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    supported_fields: Mapped[dict[str, Any] | list[str] | None] = mapped_column(
        JSON, nullable=True
    )

    protocols: Mapped[list[Protocol]] = relationship(back_populates="template")


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    inn: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    protocols: Mapped[list[Protocol]] = relationship(back_populates="owner")


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

    # JSON context with everything produced by build_protocol_context
    context: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    owner: Mapped[Owner | None] = relationship(back_populates="protocols")
    template: Mapped[Template | None] = relationship(back_populates="protocols")
    etalon: Mapped[Etalon | None] = relationship(back_populates="protocols")
