from __future__ import annotations

from sqlalchemy import JSON, Text
from sqlalchemy.types import TypeDecorator


class JSONBType(TypeDecorator):
    """JSONB-compatible type that falls back to JSON on non-Postgres DBs."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB

            return dialect.type_descriptor(JSONB(astext_type=Text()))
        return dialect.type_descriptor(JSON())
