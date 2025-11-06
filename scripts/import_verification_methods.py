from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from app.db.models import MethodologyPointType
from app.db.repositories import MethodologyPointPayload, MethodologyRepository
from app.db.session import get_sessionmaker

ALIAS_PATTERN = re.compile(r'"([^"]+)"')
TYPE_MAP = {"Yes_No": MethodologyPointType.BOOL, "Fact": MethodologyPointType.CLAUSE}
SOURCE_NOTE = (
    "Imported from verification_methods_202510201601.json (source id: {source_id})"
)


@dataclass(slots=True)
class RawMethodology:
    source_id: str
    description: str
    aliases: list[str]
    template_id: str | None
    checkups: dict[str, dict[str, str]]


def _parse_aliases(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [match.group(1).strip() for match in ALIAS_PATTERN.finditer(raw)]


def _strip_description(description: str) -> str:
    text = (description or "").strip()
    for delimiter in ('"', "\u00ab", "\u00bb"):
        index = text.find(delimiter)
        if index > 0:
            text = text[:index]
            break
    text = text.replace("\u00ab", "").replace("\u00bb", "")
    return text.strip('" ').strip()


def _guess_code(description: str, aliases: Iterable[str]) -> str:
    candidates = [alias.strip() for alias in aliases if alias.strip()]
    numeric = [alias for alias in candidates if any(char.isdigit() for char in alias)]
    if numeric:
        return min(numeric, key=len)

    header = _strip_description(description)
    if not header:
        return candidates[0] if candidates else ""

    tokens = header.split()
    if not tokens:
        return candidates[0] if candidates else header

    parts: list[str] = []
    digit_seen = False
    for token in tokens:
        token_has_digit = any(char.isdigit() for char in token)
        if digit_seen and not token_has_digit:
            break
        parts.append(token)
        if token_has_digit:
            digit_seen = True

    candidate = " ".join(parts).strip(" ,;")
    candidate = candidate or (candidates[0] if candidates else header)

    if len(candidate) <= 128:
        return candidate

    for alias in sorted(candidates, key=len):
        if len(alias) <= 128:
            return alias

    return candidate[:128].rstrip(" ,;")


def _load_raw_payload(path: Path) -> list[RawMethodology]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = []
    for item in payload.get("verification_methods", []):
        aliases = _parse_aliases(item.get("aliases"))
        checkups_raw = item.get("checkups")
        checkups = json.loads(checkups_raw) if checkups_raw else {}
        items.append(
            RawMethodology(
                source_id=item.get("id") or "",
                description=item.get("description") or "",
                aliases=aliases,
                template_id=item.get("protocol_template_id"),
                checkups=checkups,
            )
        )
    return items


def _build_points(checkups: dict[str, dict[str, str]]) -> list[MethodologyPointPayload]:
    points: list[MethodologyPointPayload] = []
    for index, (name, payload) in enumerate(checkups.items(), start=1):
        value = (payload or {}).get("Value")
        label_source = []
        if value:
            label_source.append(value.strip())
        if name:
            label_source.append(name.strip())
        label = " - ".join(filter(None, label_source)) or f"Item {index}"
        point_type = TYPE_MAP.get(
            (payload or {}).get("Type"),
            MethodologyPointType.CLAUSE,
        )
        points.append(
            MethodologyPointPayload(
                position=index,
                label=label,
                point_type=point_type,
            )
        )
    return points


async def import_verification_methods(path: Path) -> int:
    raw_items = _load_raw_payload(path)
    if not raw_items:
        return 0

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        repo = MethodologyRepository(session)
        imported = 0
        for item in raw_items:
            code = _guess_code(item.description, item.aliases)
            title = item.description or code
            points = _build_points(item.checkups)
            if not code or not points:
                continue

            methodology = await repo.upsert_methodology(
                code=code,
                title=title,
                document=None,
                notes=SOURCE_NOTE.format(source_id=item.source_id),
                allowable_variation_pct=None,
            )

            alias_payload: list[tuple[str, int]] = [(code, 100)]
            description_aliases: list[str] = []
            if item.description:
                raw_description = item.description.strip()
                if raw_description:
                    description_aliases.append(raw_description)
                stripped = _strip_description(item.description)
                if stripped and stripped != raw_description:
                    description_aliases.append(stripped)

            seen_aliases = {code}
            for alias in [*description_aliases, *item.aliases]:
                alias_clean = alias.strip()
                if not alias_clean:
                    continue
                if alias_clean in seen_aliases:
                    continue
                seen_aliases.add(alias_clean)
                alias_payload.append((alias_clean, 80))
            await repo.ensure_aliases(methodology, alias_payload)
            await repo.replace_points(methodology, points)
            imported += 1

        await session.commit()
        return imported


async def _main() -> None:
    default_path = Path("data/verification_methods_202510201601.json")
    count = await import_verification_methods(default_path)
    print(f"Imported {count} methodologies from {default_path}")


if __name__ == "__main__":
    asyncio.run(_main())
