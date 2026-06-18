import re

_STATUS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "warning",
        re.compile(
            r"(?:\bуваг\w*|\bвнимани\w*|\bwarning\b|\bжовт\w*|\bжелт\w*|\bпроблемн\w*|\bне\s+закрыт\w*|\bне\s+закрит\w*)",
            re.IGNORECASE,
        ),
    ),
    (
        "overdue",
        re.compile(
            r"(?:\bпросроч\w*|\bпростроч\w*|\boverdue\b|\bexpired\b|\bчервон\w*|\bкрасн\w*|\bкритич\w*)",
            re.IGNORECASE,
        ),
    ),
    (
        "missing",
        re.compile(r"(?:\bвідсут\w*|\bотсутств\w*|\bmissing\b|\bне\s+провед\w*)", re.IGNORECASE),
    ),
    (
        "not_issued",
        re.compile(r"(?:\bне\s+видан\w*|\bне\s+выдан\w*|\bnot_issued\b)", re.IGNORECASE),
    ),
    (
        "restricted",
        re.compile(r"(?:\bобмеж\w*|\bогранич\w*|\brestricted\b)", re.IGNORECASE),
    ),
)


def normalize_ai_status_filter_key(raw_value: str | None) -> str | None:
    """Нормалізує текст статусу до канонічного filter_key.
    Normalizes a status phrase to a canonical filter_key.
    """

    if not raw_value or not raw_value.strip():
        return None
    text = raw_value.strip()
    for filter_key, pattern in _STATUS_PATTERNS:
        if pattern.search(text):
            return filter_key
    lowered = text.lower()
    for filter_key, _pattern in _STATUS_PATTERNS:
        if lowered == filter_key:
            return filter_key
    return None


def detect_status_filter_key_from_command(raw_command: str) -> str | None:
    """Витягує filter_key статусу з тексту команди.
    Extracts a status filter_key from command text.
    """

    text = raw_command.strip()
    if not text:
        return None
    for filter_key, pattern in _STATUS_PATTERNS:
        if pattern.search(text):
            return filter_key
    status_match = re.search(
        r"(?:статус[уа]?|status)\s+([^\s,?;.]+)",
        text,
        re.IGNORECASE,
    )
    if status_match:
        return normalize_ai_status_filter_key(status_match.group(1))
    return None
