from __future__ import annotations

from io import BytesIO

from openpyxl import load_workbook


def read_column_as_list(
    file_bytes: bytes, column_letter: str = "P", start_row: int = 2
) -> list[str]:
    """
    Читает колонку (по умолчанию P) со start_row, убирает пустые и дубликаты (сохраняя порядок).
    """
    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    ws = wb.active
    items = []
    col = column_letter.upper()

    for row in range(start_row, ws.max_row + 1):
        val = ws[f"{col}{row}"].value
        if val is None:
            continue
        s = str(val).strip()
        if s:
            items.append(s)

    seen = set()
    uniq = []
    for x in items:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def read_rows_as_dicts(file_bytes: bytes) -> list[dict[str, object]]:
    """
    Читает активный лист как список словарей.
    Первая строка — это шапка (ключи), остальное — данные.
    Пустые строки пропускаются.
    """
    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    ws = wb.active

    # Шапка
    header: list[str] = []
    for cell in ws[1]:
        val = cell.value
        header.append(str(val).strip() if val is not None else "")

    rows: list[dict[str, object]] = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if all(v is None or str(v).strip() == "" for v in r):
            continue
        item: dict[str, object] = {}
        for i, key in enumerate(header):
            if not key:
                continue
            item[key] = r[i]
        rows.append(item)

    return rows
