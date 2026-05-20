import re
from datetime import datetime

from osah.domain.services.parse_ui_date_text import parse_ui_date_text


_UI_DATETIME_PATTERN = re.compile(
    r"^(?P<date>\d{1,2}[.,]\d{1,2}[.,](?:\d{2}|\d{4}))\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})$"
)
_UI_DATETIME_ERROR_TEXT = "Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ. Допустимо: 1.1.26 8:00."


# ###### РАЗБОР ДАТЫ И ВРЕМЕНИ ИЗ UI / PARSE UI DATETIME TEXT ######
def parse_ui_datetime_text(datetime_text: str) -> datetime:
    """Принимает только пользовательские форматы даты и времени и возвращает datetime.
    Accepts only user-facing date and time formats and returns a datetime object.
    """

    normalized_datetime_text = datetime_text.strip()
    if not normalized_datetime_text:
        raise ValueError(_UI_DATETIME_ERROR_TEXT)

    match = _UI_DATETIME_PATTERN.fullmatch(normalized_datetime_text)
    if match is None:
        raise ValueError(_UI_DATETIME_ERROR_TEXT)

    parsed_date = parse_ui_date_text(match.group("date"))
    hour_value = int(match.group("hour"))
    minute_value = int(match.group("minute"))
    if hour_value > 23:
        raise ValueError(_UI_DATETIME_ERROR_TEXT)
    return datetime(parsed_date.year, parsed_date.month, parsed_date.day, hour_value, minute_value)
