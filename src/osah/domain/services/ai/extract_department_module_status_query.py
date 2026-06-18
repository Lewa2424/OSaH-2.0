import re

from osah.domain.services.ai.extract_workplace_span import (
    _LOCATION_PREPOSITION_PATTERN,
    _QUOTED_SPAN_PATTERN,
    _strip_leading_location_marker,
)

_COMBO_INTENT_PATTERN = re.compile(
    r"(?:кто|хто|какие|які)"
    r".{0,120}?"
    r"(?:работает|працює|у\s+нас)",
    re.IGNORECASE | re.DOTALL,
)

_PROBLEMS_MARKER_PATTERN = re.compile(
    r"(?:"
    r"проблем\w*|"
    r"не\s+закрыт\w*|"
    r"не\s+закрит\w*|"
    r"\bуваг\w*|"
    r"\bwarning\b"
    r")",
    re.IGNORECASE,
)


def extract_department_module_status_query(raw_command: str) -> tuple[str, str, str] | None:
    """Витягує combo-запит: підрозділ + статус модуля (інструктажі/warning).
    Extracts a combo query: department span plus module status filters.
    """

    text = raw_command.strip().rstrip("?.!")
    if not text:
        return None
    if _COMBO_INTENT_PATTERN.search(text) is None:
        return None
    if _PROBLEMS_MARKER_PATTERN.search(text) is None:
        return None

    department_query = _extract_department_span(text)
    if not department_query:
        return None

    return department_query, "trainings", "warning"


def _extract_department_span(text: str) -> str | None:
    search_text = _truncate_before_problems_clause(text)

    quoted_match = _QUOTED_SPAN_PATTERN.search(search_text)
    if quoted_match is not None:
        for group_name in ("quoted", "quoted2"):
            value = quoted_match.group(group_name)
            if value is not None:
                cleaned = " ".join(value.strip().split())
                if cleaned:
                    return cleaned.rstrip("?.!,")

    preposition_matches = list(_LOCATION_PREPOSITION_PATTERN.finditer(search_text))
    if not preposition_matches:
        return None

    tail = search_text[preposition_matches[-1].end() :].strip()
    if not tail:
        return None
    return _strip_leading_location_marker(tail).rstrip("?.!,")


def _truncate_before_problems_clause(text: str) -> str:
    problems_match = _PROBLEMS_MARKER_PATTERN.search(text)
    search_text = text[: problems_match.start()] if problems_match is not None else text
    and_match = re.search(r"\s+и\s+(?:какие|які|что|що)\b", search_text, re.IGNORECASE)
    if and_match is not None:
        search_text = search_text[: and_match.start()]
    return search_text.rstrip("?.!,").strip()
