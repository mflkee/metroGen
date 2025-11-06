from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys

import asyncpg
from sqlalchemy.engine import make_url

from app.db.seed import seed_from_config


def _as_asyncpg_dsn(
    database_url: str, *, database_override: str | None = None
) -> tuple[str, str | None]:
    url = make_url(database_url)
    driver = url.drivername.split("+", 1)[0]
    target_db = database_override or url.database
    normalized = url.set(drivername=driver, database=target_db)
    return str(normalized), target_db


async def _ensure_database(
    database_url: str | None, create_if_missing: bool, verbose: bool
) -> None:
    if not database_url:
        return
    url = make_url(database_url)
    driver = url.drivername.split("+", 1)[0]
    if driver != "postgresql":
        return

    dsn, target_db = _as_asyncpg_dsn(database_url)
    try:
        conn = await asyncpg.connect(dsn)
    except asyncpg.InvalidCatalogNameError:
        if not create_if_missing:
            print(
                f"[bootstrap] database '{target_db}' does not exist. "
                "Create it manually or re-run with --create-db.",
                file=sys.stderr,
            )
            raise
        admin_db = "postgres" if target_db != "postgres" else "template1"
        admin_dsn, _ = _as_asyncpg_dsn(database_url, database_override=admin_db)
        if verbose:
            print(f"[bootstrap] creating database '{target_db}' via {admin_db}")
        admin_conn = await asyncpg.connect(admin_dsn)
        try:
            await admin_conn.execute(f'CREATE DATABASE "{target_db}"')
        finally:
            await admin_conn.close()
        if verbose:
            print(f"[bootstrap] database '{target_db}' created")
    else:
        await conn.close()


def _run_alembic(verbose: bool) -> None:
    cmd = ["alembic", "upgrade", "head"]
    if verbose:
        print(f"[bootstrap] running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, env=os.environ.copy())
    except subprocess.CalledProcessError as exc:
        print(f"[bootstrap] alembic failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc


async def _seed(verbose: bool) -> None:
    if verbose:
        print("[bootstrap] seeding owners and base methodologies")
    result = await seed_from_config()
    if verbose:
        owners = result.get("owners", 0)
        methodologies = result.get("methodologies", 0)
        print(f"[bootstrap] ensured {owners} owners, {methodologies} methodologies")


async def _run(args: argparse.Namespace) -> None:
    database_url = os.environ.get("DATABASE_URL")
    try:
        await _ensure_database(database_url, args.create_db, args.verbose)
    except asyncpg.InvalidCatalogNameError as exc:
        if args.verbose:
            print("[bootstrap] stopping because target database is missing", file=sys.stderr)
        raise SystemExit(1) from exc

    _run_alembic(args.verbose)

    if not args.skip_seed:
        await _seed(args.verbose)
    elif args.verbose:
        print("[bootstrap] skipping seed step")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply migrations and seed default data for the metrologenerator database."
    )
    parser.add_argument(
        "--create-db",
        action="store_true",
        help="Create the DATABASE_URL database automatically if it does not exist.",
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="Skip seeding owners and base methodologies.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress information.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.verbose:
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            print(f"[bootstrap] DATABASE_URL={database_url}")
        else:
            print(
                "[bootstrap] DATABASE_URL not set, relying on default sqlite fallback",
                file=sys.stderr,
            )
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
