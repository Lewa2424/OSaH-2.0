import re

_PPE_NOISE_TOKEN_PATTERN = re.compile(
    r"\b(?:зіз|сиз|ppe|спецодяг|спецодежда|средств\w*\s+защит\w*)\b",
    re.IGNORECASE,
)


def normalize_ppe_item_query(item_query: str) -> str:
    """Прибирає службові слова на кшталт «ЗІЗ» з запиту предмета.
    Removes service words like 'PPE' from an item query string.
    """

    cleaned = _PPE_NOISE_TOKEN_PATTERN.sub(" ", item_query)
    return " ".join(cleaned.split()).strip()
