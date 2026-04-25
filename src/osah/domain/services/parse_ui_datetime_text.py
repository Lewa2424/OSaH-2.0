from datetime import datetime


# ###### РОЗБІР ДАТИ Й ЧАСУ З UI / PARSE UI DATETIME TEXT ######
def parse_ui_datetime_text(datetime_text: str) -> datetime:
    """Приймає ДД.MM.ГГГГ HH:MM та сумісні legacy-формати і повертає datetime.
    Accepts DD.MM.YYYY HH:MM and compatible legacy formats, returning datetime.
    """

    normalized_datetime_text = datetime_text.strip()
    if not normalized_datetime_text:
        raise ValueError("Дата й час обов'язкові у форматі ДД.ММ.РРРР HH:MM.")
    for format_pattern in ("%d.%m.%Y %H:%M", "%d:%m:%Y %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(normalized_datetime_text, format_pattern)
        except ValueError:
            continue
    raise ValueError("Дата й час мають бути у форматі ДД.ММ.РРРР HH:MM.")
