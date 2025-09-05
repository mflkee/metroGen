import io

from openpyxl import Workbook

from app.utils.excel import read_column_as_list


def test_read_column_as_list_default():
    wb = Workbook()
    ws = wb.active
    ws["P1"] = "Номер свидетельтсва"
    ws["P2"] = "С-ЕЖБ/05-06-2025/440144576"
    ws["P3"] = "С-ЕЖБ/05-06-2025/440144575"
    ws["P4"] = "С-ЕЖБ/05-06-2025/440144575"  # дубликат
    buf = io.BytesIO()
    wb.save(buf)

    items = read_column_as_list(buf.getvalue(), column_letter="P", start_row=2)
    assert items == [
        "С-ЕЖБ/05-06-2025/440144576",
        "С-ЕЖБ/05-06-2025/440144575",
    ]
