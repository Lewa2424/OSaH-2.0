"""Маркери відносної дати в AI-командах.
Relative date markers in AI command phrases.
"""

from __future__ import annotations

import re

_CURRENT_DATE_PATTERN = re.compile(
    r"(?:"
    r"\b(?:сьогодні|сегодня|today|сегодняшн\w*|"
    r"текущ\w*|поточн\w*|current\s+date)\b|"
    r"(?:с|з|со)\s+(?:текущ|поточн)\w*\s+дат"
    r")",
    re.IGNORECASE,
)

_DATE_ANSWER_PATTERN = re.compile(
    r"(?:"
    r"^\s*\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?\s*$|"
    r"^\s*\d{1,2}\s+[а-яіїєґ]+\s*$"
    r")",
    re.IGNORECASE,
)


def mentions_current_date(raw_command: str) -> bool:
    """Перевіряє, чи фраза посилається на сьогоднішню дату.
    Checks whether the phrase refers to today's date.
    """

    return bool(_CURRENT_DATE_PATTERN.search(raw_command.strip()))


def looks_like_date_answer(answer_text: str) -> bool:
    """Перевіряє, чи відповідь схожа на дату або відносний маркер дати.
    Checks whether an answer looks like a date or relative date marker.
    """

    normalized = answer_text.strip()
    if not normalized:
        return False
    if mentions_current_date(normalized):
        return True
    if _DATE_ANSWER_PATTERN.fullmatch(normalized):
        return True
    lowered = normalized.lower()
    return lowered in {"сьогодні", "сегодня", "today", "завтра", "вчора", "вчера"}
