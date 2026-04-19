from pathlib import Path
from zipfile import ZipFile

from osah.infrastructure.importing.normalize_employee_import_row_dict import normalize_employee_import_row_dict
from osah.infrastructure.importing.read_xlsx_shared_strings import read_xlsx_shared_strings
from osah.infrastructure.importing.read_xlsx_worksheet_rows import read_xlsx_worksheet_rows
from osah.infrastructure.importing.resolve_first_xlsx_worksheet_path import resolve_first_xlsx_worksheet_path


# ###### ЧИТАННЯ РЯДКІВ ПРАЦІВНИКІВ З XLSX / ЧТЕНИЕ СТРОК СОТРУДНИКОВ ИЗ XLSX ######
def read_employee_rows_from_xlsx_file(source_path: Path) -> tuple[dict[str, str], ...]:
    """Повертає рядки імпорту працівників із першого аркуша XLSX-файлу.
    Возвращает строки импорта сотрудников с первого листа XLSX-файла.
    """

    with ZipFile(source_path, mode="r") as archive:
        shared_strings = read_xlsx_shared_strings(archive)
        worksheet_path = resolve_first_xlsx_worksheet_path(archive)
        worksheet_rows = read_xlsx_worksheet_rows(archive, worksheet_path, shared_strings)

    if not worksheet_rows:
        return ()
    header_row = tuple(header_text.strip() for header_text in worksheet_rows[0])
    normalized_rows: list[dict[str, str]] = []
    for row_values in worksheet_rows[1:]:
        row_dict = {
            header_row[column_index]: row_values[column_index]
            for column_index in range(min(len(header_row), len(row_values)))
            if header_row[column_index]
        }
        normalized_rows.append(normalize_employee_import_row_dict(row_dict))
    return tuple(normalized_rows)
