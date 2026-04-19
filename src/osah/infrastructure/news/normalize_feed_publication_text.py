from datetime import datetime
from email.utils import parsedate_to_datetime


# ###### НОРМАЛІЗАЦІЯ ДАТИ ПУБЛІКАЦІЇ FEED / НОРМАЛИЗАЦИЯ ДАТЫ ПУБЛИКАЦИИ FEED ######
def normalize_feed_publication_text(raw_publication_text: str) -> str:
    """Перетворює дати RSS або Atom до стабільного ISO-формату.
    Преобразует даты RSS или Atom к стабильному ISO-формату.
    """

    normalized_text = raw_publication_text.strip()
    if not normalized_text:
        return ""
    try:
        return parsedate_to_datetime(normalized_text).isoformat(timespec="seconds")
    except (TypeError, ValueError, IndexError, OverflowError):
        pass
    try:
        return datetime.fromisoformat(normalized_text.replace("Z", "+00:00")).isoformat(timespec="seconds")
    except ValueError:
        return normalized_text
