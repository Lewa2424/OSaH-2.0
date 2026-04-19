# ###### НОРМАЛІЗАЦІЯ СТАТУСУ ЗАЙНЯТОСТІ ІМПОРТУ / НОРМАЛИЗАЦИЯ СТАТУСА ЗАНЯТОСТИ ИМПОРТА ######
def normalize_import_employment_status(employment_status_text: str) -> str:
    """Повертає технічне значення статусу зайнятості з вільного тексту імпорту.
    Возвращает техническое значение статуса занятости из свободного текста импорта.
    """

    normalized_text = employment_status_text.strip().lower()
    if normalized_text in {"active", "активний", "активна", "працює", "работает"}:
        return "active"
    if normalized_text in {"archived", "archive", "архів", "архив", "звільнений", "уволен"}:
        return "archived"
    return ""
