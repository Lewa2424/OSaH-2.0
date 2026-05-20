import re
from datetime import date


_UI_DATE_PATTERN = re.compile(r"^(?P<day>\d{1,2})(?P<sep>[.,])(?P<month>\d{1,2})(?P=sep)(?P<year>\d{2}|\d{4})$")
_UI_DATE_ERROR_TEXT = "Введите дату в формате ДД.ММ.ГГГГ. Допустимо: 1.1.26 или 01,01,2026."


# ###### РАЗБОР ДАТЫ ИЗ UI / PARSE UI DATE TEXT ######
def parse_ui_date_text(date_text: str) -> date:
    """Принимает только пользовательские форматы даты и возвращает date.
    Accepts only user-facing date formats and returns a date object.
    """

    normalized_date_text = date_text.strip()
    if not normalized_date_text:
        raise ValueError(_UI_DATE_ERROR_TEXT)

    match = _UI_DATE_PATTERN.fullmatch(normalized_date_text)
    if match is None:
        raise ValueError(_UI_DATE_ERROR_TEXT)

    year_text = match.group("year")
    year_value = 2000 + int(year_text) if len(year_text) == 2 else int(year_text)
    try:
        return date(year_value, int(match.group("month")), int(match.group("day")))
    except ValueError as error:
        raise ValueError(_UI_DATE_ERROR_TEXT) from error
