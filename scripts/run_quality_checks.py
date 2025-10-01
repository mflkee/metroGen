from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DEFAULT_SQLITE = "sqlite+aiosqlite:///./dev.db"
ENV_FILE = Path(".env")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _can_connect(url: str) -> bool:
    async def _check() -> bool:
        engine = create_async_engine(url)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
        finally:
            await engine.dispose()

    try:
        return asyncio.run(_check())
    except Exception:
        return False


def ensure_database_url() -> None:
    url = os.environ.get("DATABASE_URL")
    if url and url.startswith("postgresql"):
        if _can_connect(url):
            return
        print("[warn] PostgreSQL URL set but unreachable; falling back to sqlite dev.db")
    elif url:
        return
    else:
        print("[warn] DATABASE_URL not set; using sqlite dev.db")

    os.environ["DATABASE_URL"] = DEFAULT_SQLITE


def run_command(
    command: Sequence[str],
    *,
    description: str,
    allow_failure: bool = False,
) -> tuple[bool, str]:
    print(f"\n==> {description}")
    print("   $", " ".join(shlex.quote(c) for c in command))
    result = subprocess.run(command, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    success = result.returncode == 0
    if not success and not allow_failure:
        print(f"[!] step failed (exit code {result.returncode})")
    return success, description


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Ruff checks, apply fixes (unless --no-fix), and execute pytest",
    )
    parser.add_argument(
        "--no-fix",
        action="store_true",
        help="Do not run Ruff auto-fix commands",
    )
    parser.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        help="Additional pytest arguments (everything after this flag)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    load_env_file(ENV_FILE)
    ensure_database_url()

    summary: list[tuple[str, bool]] = []
    failure = False

    success, desc = run_command(
        ["ruff", "format", "--check", "."],
        description="Ruff format check",
        allow_failure=True,
    )
    summary.append((desc, success))
    if not success and not args.no_fix:
        run_command(
            ["ruff", "format", "."],
            description="Ruff format auto-fix",
            allow_failure=True,
        )
        success, desc = run_command(
            ["ruff", "format", "--check", "."],
            description="Ruff format re-check",
            allow_failure=False,
        )
        summary.append((desc, success))
    failure = failure or not success

    success, desc = run_command(
        ["ruff", "check", "."],
        description="Ruff lint check",
        allow_failure=True,
    )
    summary.append((desc, success))
    if not success and not args.no_fix:
        run_command(
            ["ruff", "check", "--fix", "."],
            description="Ruff lint auto-fix",
            allow_failure=True,
        )
        success, desc = run_command(
            ["ruff", "check", "."],
            description="Ruff lint re-check",
            allow_failure=False,
        )
        summary.append((desc, success))
    failure = failure or not success

    pytest_cmd = ["pytest", "-q"]
    if args.pytest_args:
        pytest_cmd.extend(args.pytest_args)
    success, desc = run_command(pytest_cmd, description="Pytest suite")
    summary.append((desc, success))
    failure = failure or not success

    print("\nSummary:")
    for step, ok in summary:
        status = "OK" if ok else "FAIL"
        print(f" - {step}: {status}")

    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
