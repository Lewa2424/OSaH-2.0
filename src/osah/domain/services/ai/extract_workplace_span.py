import re

_DEPARTMENT_LIST_INTENT = re.compile(
    r"(?:кто|хто|какие|які)"
    r".{0,80}?"
    r"(?:работает|працює|у\s+нас|список\s+(?:сотрудник|працівник))",
    re.IGNORECASE | re.DOTALL,
)

_QUOTED_SPAN_PATTERN = re.compile(
    r"(?:\bв\b|\bу\b|\bна\b)\s+"
    r"(?:«\s*(?P<quoted>[^»\"]{2,80})\s*»|\"\s*(?P<quoted2>[^\"]{2,80})\s*\")",
    re.IGNORECASE,
)

_LOCATION_PREPOSITION_PATTERN = re.compile(r"(?:^|\s)(?:в|у|на)\s+", re.IGNORECASE)


def matches_department_employees_intent(raw_command: str) -> bool:
    """Перевіряє намір запиту списку працівників підрозділу.
    Checks intent for a department employee list query.
    """

    text = raw_command.strip()
    if not text:
        return False
    return _DEPARTMENT_LIST_INTENT.search(text) is not None


def extract_workplace_span(raw_command: str) -> str | None:
    """Витягує фрагмент назви підрозділу/служби після маркера локації.
    Extracts a department or workplace name span after a location marker.
    """

    text = raw_command.strip().rstrip("?.!")
    if not text or not matches_department_employees_intent(text):
        return None

    quoted_match = _QUOTED_SPAN_PATTERN.search(text)
    if quoted_match is not None:
        for group_name in ("quoted", "quoted2"):
            value = quoted_match.group(group_name)
            if value is not None:
                cleaned = " ".join(value.strip().split())
                if cleaned:
                    return cleaned

    preposition_matches = list(_LOCATION_PREPOSITION_PATTERN.finditer(text))
    if not preposition_matches:
        return None

    tail = text[preposition_matches[-1].end() :].strip()
    if not tail:
        return None
    return _strip_leading_location_marker(tail)


def _strip_leading_location_marker(value: str) -> str:
    tokens = value.split()
    if len(tokens) <= 1:
        return value

    first = tokens[0].lower().rstrip(".")
    strip_markers = {
        "подразделении",
        "подразделение",
        "підрозділі",
        "підрозділ",
        "дільниці",
        "дільниця",
        "отделе",
        "отдел",
        "цехе",
        "цех",
        "лаборатории",
        "лабораторія",
        "лаборатории",
    }
    if first in strip_markers:
        remainder = " ".join(tokens[1:]).strip()
        return remainder or value
    return value
