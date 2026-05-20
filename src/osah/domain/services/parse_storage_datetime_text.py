from datetime import datetime


# ###### РАЗБОР DATETIME ИЗ STORAGE / PARSE STORAGE DATETIME TEXT ######
def parse_storage_datetime_text(value: str | datetime) -> datetime:
    """Принимает только persisted datetime-значения и возвращает datetime.
    Accepts only persisted datetime values and returns a datetime object.
    """

    if isinstance(value, datetime):
        return value

    normalized_text = value.strip()
    if not normalized_text:
        raise ValueError("Storage datetime must not be empty.")
    if normalized_text.endswith("Z"):
        normalized_text = f"{normalized_text[:-1]}+00:00"
    if "T" in normalized_text and " " not in normalized_text:
        normalized_text = normalized_text.replace("T", " ", 1)

    parsed_value = datetime.fromisoformat(normalized_text)
    if parsed_value.tzinfo is not None:
        parsed_value = parsed_value.astimezone().replace(tzinfo=None)
    return parsed_value
