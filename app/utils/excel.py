from __future__ import annotations
from io import BytesIO
from typing import List
from openpyxl import load_workbook

def read_column_as_list(file_bytes: bytes, column_letter: str = "P", start_row: int = 2) -> List[str]:
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
