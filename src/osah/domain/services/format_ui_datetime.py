from datetime import datetime

from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


# ###### ФОРМАТ ДАТЫ И ВРЕМЕНИ ДЛЯ UI / FORMAT UI DATETIME ######
def format_ui_datetime(value: str | datetime) -> str:
    """Возвращает дату и время в формате DD.MM.YYYY HH:MM для UI.
    Returns a DD.MM.YYYY HH:MM string for UI display.
    """

    if isinstance(value, str):
        normalized_text = value.strip()
        if not normalized_text or normalized_text == "-":
            return normalized_text or "-"
    try:
        return parse_storage_datetime_text(value).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return ""
