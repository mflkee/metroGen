from __future__ import annotations
# isort: skip_file

import os
import sys
import asyncio
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db import models as _models  # noqa: E402,F401  # register models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def get_url() -> str:
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    settings_url = getattr(settings, "DATABASE_URL", None)
    if settings_url:
        return settings_url

    # fallback for local runs
    return "sqlite:///dev.db"


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    if url.startswith("postgresql+asyncpg"):

        async def async_run() -> None:
            connectable: AsyncEngine = create_async_engine(url, poolclass=pool.NullPool)
            async with connectable.connect() as connection:
                await connection.run_sync(_run_migrations)
            await connectable.dispose()

        asyncio.run(async_run())
        return

    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        _run_migrations(connection)


def _run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
