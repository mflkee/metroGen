from __future__ import annotations

from . import utils

__all__ = ("utils",)

try:  # pragma: no cover - executed only when SQLAlchemy installed
    from .core import (
        AuxiliaryInstrumentRepository,
        BaseRepository,
        EtalonRepository,
        InstrumentRepository,
        MethodologyPointPayload,
        MethodologyRepository,
        OwnerRepository,
        RegistryRepository,
        UserRepository,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    if exc.name != "sqlalchemy":
        raise
else:  # pragma: no cover - skip when SQLAlchemy missing in tests
    __all__ += (
        "BaseRepository",
        "AuxiliaryInstrumentRepository",
        "EtalonRepository",
        "InstrumentRepository",
        "MethodologyPointPayload",
        "MethodologyRepository",
        "OwnerRepository",
        "RegistryRepository",
        "UserRepository",
    )
