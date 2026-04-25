from datetime import datetime, date


# ###### РОЗБІР ДАТИ З UI / PARSE UI DATE TEXT ######
def parse_ui_date_text(date_text: str) -> date:
    """Приймає ДД.MM.ГГГГ та сумісні legacy-формати і повертає об'єкт date.
    Accepts DD.MM.YYYY and compatible legacy formats, returning a date object.
    """

    normalized_date_text = date_text.strip()
    if not normalized_date_text:
        raise ValueError("Дата обов'язкова у форматі ДД.ММ.РРРР.")
    for format_pattern in ("%d.%m.%Y", "%d:%m:%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(normalized_date_text, format_pattern).date()
        except ValueError:
            continue
    raise ValueError("Дата має бути у форматі ДД.ММ.РРРР.")
