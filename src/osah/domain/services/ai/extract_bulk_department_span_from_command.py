import re

_LOCATION_PREPOSITION_PATTERN = re.compile(
    r"(?:^|\s)(?:в|у|на)\s+",
    re.IGNORECASE,
)

_BULK_DEPARTMENT_MARKER_PATTERN = re.compile(
    r"(?:"
    r"подразделени[яе]?|підрозділ[уа]?|отдел[уа]?|"
    r"дільниц[іи]|участк[ае]|цех[уа]?|служб[аи]"
    r")",
    re.IGNORECASE,
)

_DATIVE_DEPARTMENT_PATTERN = re.compile(
    r"(?:"
    r"всему|усім|всім|всем"
    r")\s+"
    r"(?:"
    r"подразделени[яею]?|підрозділ[уа]?|отдел[уа]?|"
    r"дільниц[іи]|участк[ае]|цех[уа]?|служб[аи]"
    r")\s+"
    r"(.+?)"
    r"(?=\s+(?:"
    r"дополнительно|додатково|видай|выдай|занеси|занести|проведи|додай|добавь|"
    r"по\s+\d|по\s+пар|за\s+|сьогодні|сегодня|today|каск|перчатк|рукавиц|ботинк|інструктаж|инструктаж|мед"
    r")|$)",
    re.IGNORECASE,
)

_ITEM_STOP_PATTERN = re.compile(
    r"\s+(?:"
    r"каск\w*|перчатк\w*|рукавиц\w*|ботинк\w*|черевик\w*|"
    r"інструктаж\w*|инструктаж\w*|мед\w*"
    r")\b",
    re.IGNORECASE,
)

_STRIP_LOCATION_MARKERS = frozenset(
    {
        "подразделении",
        "подразделение",
        "підрозділі",
        "підрозділ",
        "дільниці",
        "дільниця",
        "отделе",
        "отдел",
        "цехе",
        "цеху",
        "цех",
        "службе",
        "служба",
        "участке",
        "участок",
    }
)


def extract_bulk_department_span_from_command(raw_command: str) -> str | None:
    """Витягує фрагмент підрозділу для bulk-команд «всем в цеху …».
    Extracts a department span for bulk commands like give-to-all-in-department.
    """

    text = raw_command.strip().rstrip("?.!")
    if not text:
        return None

    dative_match = _DATIVE_DEPARTMENT_PATTERN.search(text)
    if dative_match is not None:
        cleaned = _clean_span(dative_match.group(1))
        if cleaned:
            return cleaned

    if not _BULK_DEPARTMENT_MARKER_PATTERN.search(text):
        return None

    preposition_matches = list(_LOCATION_PREPOSITION_PATTERN.finditer(text))
    if not preposition_matches:
        return None

    for match in reversed(preposition_matches):
        tail = text[match.end() :].strip()
        if not tail or not _BULK_DEPARTMENT_MARKER_PATTERN.match(tail):
            continue
        span = _strip_leading_location_marker(tail)
        cleaned = _clean_span(span)
        if cleaned:
            return cleaned

    return None


def _strip_leading_location_marker(value: str) -> str:
    tokens = value.split()
    if len(tokens) <= 1:
        return value
    first = tokens[0].lower().rstrip(".")
    if first in _STRIP_LOCATION_MARKERS:
        remainder = " ".join(tokens[1:]).strip()
        return remainder or value
    return value


def _clean_span(value: str) -> str | None:
    cleaned = value.strip(" ,.;:")
    item_stop = _ITEM_STOP_PATTERN.search(cleaned)
    if item_stop is not None:
        cleaned = cleaned[: item_stop.start()].strip(" ,.;:")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None
