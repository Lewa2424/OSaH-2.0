import re
from datetime import date, datetime


_STORAGE_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ###### РАЗБОР ДАТЫ ИЗ STORAGE / PARSE STORAGE DATE TEXT ######
def parse_storage_date_text(value: str | date | datetime) -> date:
    """Принимает только persisted date-значения и возвращает date.
    Accepts only persisted date values and returns a date object.
    """

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    normalized_text = value.strip()
    if not _STORAGE_DATE_PATTERN.fullmatch(normalized_text):
        raise ValueError("Storage date must use YYYY-MM-DD.")
    return date.fromisoformat(normalized_text)
