import re


_EXPORTABLE_TABLE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_EXCLUDED_EXPORT_TABLES: frozenset[str] = frozenset({"app_settings"})


# ###### ПЕРЕВІРКА ДОЗВОЛЕНОЇ ТАБЛИЦІ ДЛЯ ЕКСПОРТУ / EXPORTABLE TABLE NAME CHECK ######
def is_exportable_table_name(table_name: str) -> bool:
    """Повертає True, якщо таблицю можна безпечно включити в JSON-експорт.
    Returns True when a table can be safely included in JSON export.
    """

    normalized_name = table_name.strip()
    if normalized_name in _EXCLUDED_EXPORT_TABLES:
        return False
    return bool(_EXPORTABLE_TABLE_NAME_PATTERN.fullmatch(normalized_name))
