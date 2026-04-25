from datetime import date


# ###### ФОРМАТ ДАТИ ДЛЯ UI / FORMAT UI DATE ######
def format_ui_date(date_text: str) -> str:
    """Повертає дату у форматі ДД.MM.ГГГГ для показу в інтерфейсі.
    Returns a date in DD.MM.YYYY format for UI display.
    """

    normalized_date_text = date_text.strip()
    if not normalized_date_text or normalized_date_text == "-":
        return normalized_date_text or "-"
    try:
        return date.fromisoformat(normalized_date_text).strftime("%d.%m.%Y")
    except ValueError:
        return normalized_date_text
