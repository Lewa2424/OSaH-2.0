from osah.infrastructure.importing.build_employee_import_header_map import build_employee_import_header_map


# ###### НОРМАЛІЗАЦІЯ РЯДКА ІМПОРТУ ПРАЦІВНИКА / НОРМАЛИЗАЦИЯ СТРОКИ ИМПОРТА СОТРУДНИКА ######
def normalize_employee_import_row_dict(row_data: dict[str, str]) -> dict[str, str]:
    """Повертає рядок імпорту працівника з нормалізованими технічними ключами.
    Возвращает строку импорта сотрудника с нормализованными техническими ключами.
    """

    header_map = build_employee_import_header_map()
    normalized_row: dict[str, str] = {}
    for raw_key, raw_value in row_data.items():
        normalized_key = header_map.get(raw_key.strip().lower())
        if normalized_key is None:
            continue
        normalized_row[normalized_key] = raw_value.strip()
    return normalized_row
