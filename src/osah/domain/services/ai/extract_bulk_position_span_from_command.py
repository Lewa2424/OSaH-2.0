import re

_POSITION_DUTY_PATTERN = re.compile(
    r"(?:"
    r"(?:в|на)\s+должност[иь]\s+"
    r"|"
    r"должност[иь]\s+"
    r")"
    r"(.+?)"
    r"(?=\s+(?:"
    r"дополнительно|додатково|видай|выдай|занеси|занести|проведи|додай|добавь|"
    r"по\s+\d|по\s+пар|за\s+|сьогодні|сегодня|today|каск|перчатк|рукавиц|ботинк|інструктаж|инструктаж|мед"
    r")|$)",
    re.IGNORECASE,
)

_POSITION_DUTY_UK_PATTERN = re.compile(
    r"(?:"
    r"(?:на|у)\s+посад[іи]\s+"
    r"|"
    r"посад[іи]\s+"
    r")"
    r"(.+?)"
    r"(?=\s+(?:"
    r"дополнительно|додатково|видай|выдай|занеси|занести|проведи|додай|добавь|"
    r"по\s+\d|по\s+пар|за\s+|сьогодні|сегодня|today|каск|перчатк|рукавиц|ботинк|інструктаж|инструктаж|мед"
    r")|$)",
    re.IGNORECASE,
)

_ALL_TO_PROFESSION_PATTERN = re.compile(
    r"(?:"
    r"(?:всім|усім|всем|працівникам|работникам)\s+"
    r"(стропальник\w*|докер\w*|зварник\w*|сварщик\w*|комірник\w*|електромонтер\w*)"
    r"|"
    r"(?:всім|усім|всем)\s+([а-яіїєґa-z-]{4,30}(?:никам|ників|щикам|щиків|ам|ів))\b"
    r")",
    re.IGNORECASE,
)


def extract_bulk_position_span_from_command(raw_command: str) -> str | None:
    """Витягує фрагмент посади для bulk-команд «всем в должности …».
    Extracts a position span for bulk give-to-all-by-position commands.
    """

    text = raw_command.strip().rstrip("?.!")
    if not text:
        return None

    for pattern in (_POSITION_DUTY_PATTERN, _POSITION_DUTY_UK_PATTERN):
        match = pattern.search(text)
        if match is not None:
            cleaned = _clean_span(match.group(1))
            if cleaned:
                return cleaned

    profession_match = _ALL_TO_PROFESSION_PATTERN.search(text)
    if profession_match is not None:
        for group in profession_match.groups():
            if group and group.strip():
                return group.strip()

    return None


def _clean_span(value: str) -> str | None:
    cleaned = value.strip(" ,.;:")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None
