import json
from pathlib import Path

from osah.infrastructure.importing.normalize_employee_import_row_dict import normalize_employee_import_row_dict


# ###### ЧИТАННЯ РЯДКІВ ПРАЦІВНИКІВ З JSON / ЧТЕНИЕ СТРОК СОТРУДНИКОВ ИЗ JSON ######
def read_employee_rows_from_json_file(source_path: Path) -> tuple[dict[str, str], ...]:
    """Повертає рядки імпорту працівників із JSON-файлу.
    Возвращает строки импорта сотрудников из JSON-файла.
    """

    parsed_payload = json.loads(source_path.read_text(encoding="utf-8"))
    if isinstance(parsed_payload, dict):
        raw_rows = parsed_payload.get("employees", ())
    else:
        raw_rows = parsed_payload
    if not isinstance(raw_rows, list):
        raise ValueError("JSON-імпорт працівників має містити масив записів.")

    normalized_rows: list[dict[str, str]] = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict):
            raise ValueError("Кожен JSON-запис імпорту має бути об'єктом.")
        normalized_rows.append(
            normalize_employee_import_row_dict(
                {str(key): str(value) for key, value in raw_row.items() if value is not None}
            )
        )
    return tuple(normalized_rows)
