from datetime import datetime


# ###### ФОРМАТ ДАТИ Й ЧАСУ ДЛЯ UI / FORMAT UI DATETIME ######
def format_ui_datetime(datetime_text: str) -> str:
    """Повертає дату й час у форматі ДД.MM.ГГГГ HH:MM для показу в інтерфейсі.
    Returns a datetime in DD.MM.YYYY HH:MM format for UI display.
    """

    normalized_datetime_text = datetime_text.strip()
    if not normalized_datetime_text or normalized_datetime_text == "-":
        return normalized_datetime_text or "-"
    try:
        return datetime.fromisoformat(normalized_datetime_text).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return normalized_datetime_text
