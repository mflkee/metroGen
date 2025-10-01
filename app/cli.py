from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from app.db.session import get_sessionmaker
from app.services.registry_ingest import (
    REGISTRY_SERIAL_KEYS,
    ingest_registry_rows,
)
from app.utils.excel import read_rows_with_required_headers


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="metrologenerator", description="Utility commands")
    sub = parser.add_subparsers(dest="command", required=True)

    import_parser = sub.add_parser(
        "import-registry",
        help="Импортирует Excel с реестром поверок в базу данных",
    )
    import_parser.add_argument("file", help="Путь к Excel-файлу реестра")
    import_parser.add_argument(
        "--source-sheet",
        dest="source_sheet",
        default=None,
        help="Имя листа (если нужен конкретный)",
    )
    import_parser.add_argument(
        "--instrument-kind",
        dest="instrument_kind",
        default=None,
        help="Тип средств измерений (controllers, manometers и т.д.)",
    )
    import_parser.add_argument(
        "--header-row",
        dest="header_row",
        type=int,
        default=5,
        help="Номер строки с заголовками (по умолчанию 5)",
    )
    import_parser.add_argument(
        "--data-start-row",
        dest="data_start_row",
        type=int,
        default=6,
        help="Номер строки с данными (по умолчанию 6)",
    )

    return parser


async def _run_import_registry(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if not path.exists():
        raise FileNotFoundError(f"registry file not found: {path}")

    payload = path.read_bytes()
    rows = read_rows_with_required_headers(
        payload,
        header_row=args.header_row,
        data_start_row=args.data_start_row,
        required_headers=REGISTRY_SERIAL_KEYS,
    )
    if not rows:
        raise ValueError("registry file has no recognizable serial number columns")

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        result = await ingest_registry_rows(
            session,
            source_file=path.name,
            rows=rows,
            source_sheet=args.source_sheet,
            instrument_kind=args.instrument_kind,
        )
        await session.commit()

    print(
        "Imported",
        result["processed"],
        "rows (deactivated:",
        result["deactivated"],
        ")",
    )


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "import-registry":
        asyncio.run(_run_import_registry(args))
    else:  # pragma: no cover - defensive; argparse enforces known commands
        parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - manual invocation helper
    main()
