from datetime import date, datetime

from osah.domain.services.parse_storage_date_text import parse_storage_date_text


# ###### ФОРМАТ ДАТЫ ДЛЯ UI / FORMAT UI DATE ######
def format_ui_date(value: str | date | datetime) -> str:
    """Возвращает дату в формате DD.MM.YYYY для UI.
    Returns a DD.MM.YYYY string for UI display.
    """

    if isinstance(value, str):
        normalized_text = value.strip()
        if not normalized_text or normalized_text == "-":
            return normalized_text or "-"
    try:
        return parse_storage_date_text(value).strftime("%d.%m.%Y")
    except ValueError:
        return ""
