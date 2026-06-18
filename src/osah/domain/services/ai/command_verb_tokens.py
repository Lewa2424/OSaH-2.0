"""Токени командних дієслів, які не можуть бути employee_query.
Command verb tokens that must never be treated as employee_query.
"""

from __future__ import annotations

import re

_COMMAND_VERB_TOKENS: frozenset[str] = frozenset(
    {
        "занеси",
        "занести",
        "внеси",
        "внести",
        "проведи",
        "провести",
        "оформи",
        "оформить",
        "выдай",
        "видай",
        "выдать",
        "видати",
        "дай",
        "дайте",
        "раздай",
        "раздайте",
        "впиши",
        "выпиши",
        "запиши",
        "добавь",
        "добавить",
        "додай",
        "додати",
        "створи",
        "создай",
        "создать",
        "поставь",
        "постав",
        "забей",
        "онови",
        "обнови",
        "обновить",
        "зміни",
        "измени",
        "продли",
        "продлить",
        "продовж",
        "продовжити",
        "подовж",
        "подовжити",
        "открой",
        "открыть",
        "откройте",
        "відкрий",
        "відкрити",
        "покажи",
        "показать",
        "показати",
        "выведи",
        "вывести",
        "виведи",
        "найди",
        "знайди",
        "open",
    }
)

_NAV_VERB_PATTERN = re.compile(
    r"^\s*(?:"
    r"покажи|показати|показать|"
    r"відкрий|відкрити|"
    r"открой|открыть|откройте|"
    r"выведи|вывести|виведи|"
    r"open"
    r")\b",
    re.IGNORECASE,
)

_PPE_NOISE_TOKEN_PATTERN = re.compile(
    r"^(?:"
    r"каск\w*|черевик\w*|ботинк\w*|рукавиц\w*|перчат\w*|"
    r"жилет\w*|комбінезон\w*|роб\w*|спецодяг\w*|взутт\w*|обув\w*|"
    r"зіз|зиз|сиз|ppe"
    r")$",
    re.IGNORECASE,
)

_TRAINING_NOISE_TOKEN_PATTERN = re.compile(
    r"^(?:"
    r"первичн\w*|повторн\w*|первинн\w*|цільов\w*|целев\w*|"
    r"инструктаж\w*|інструктаж\w*|"
    r"текущ\w*|сегодняшн\w*|сьогоднішн\w*"
    r")$",
    re.IGNORECASE,
)

_EMPLOYEE_QUERY_STOP_WORDS = frozenset(
    {
        "сьогодні",
        "сегодня",
        "today",
        "tomorrow",
        "завтра",
        "вчора",
        "вчера",
        "если",
        "якщо",
        "можно",
        "можна",
        "за",
        "для",
        "for",
        "на",
        "по",
        "з",
        "із",
        "из",
        "і",
        "и",
        "та",
        "the",
    }
)


def is_command_verb_token(token: str) -> bool:
    """Перевіряє, чи токен є командним дієслом.
    Checks whether a token is a command verb.
    """

    return token.strip().lower() in _COMMAND_VERB_TOKENS


def has_nav_verb_lead(raw_command: str) -> bool:
    """Перевіряє, чи команда починається з nav-дієслова.
    Checks whether the command starts with a navigation verb.
    """

    return bool(_NAV_VERB_PATTERN.search(raw_command.strip()))


def is_training_noise_token(token: str) -> bool:
    """Перевіряє, чи токен описує тип інструктажу або дату, а не ПІБ.
    Checks whether a token is training-type or date noise rather than a name part.
    """

    return bool(_TRAINING_NOISE_TOKEN_PATTERN.fullmatch(token.strip()))


def is_employee_query_stop_word(value: str | None) -> bool:
    """Перевіряє, чи фрагмент — службове слово, а не ПІБ працівника.
    Checks whether a fragment is a service token rather than an employee name.
    """

    if not value or not value.strip():
        return True
    normalized = value.strip().lower()
    if normalized in _EMPLOYEE_QUERY_STOP_WORDS:
        return True
    if is_command_verb_token(normalized):
        return True
    if is_training_noise_token(normalized):
        return True
    return bool(_PPE_NOISE_TOKEN_PATTERN.fullmatch(value.strip()))


def filter_valid_employee_query_tokens(values: tuple[str, ...]) -> tuple[str, ...]:
    """Прибирає службові токени зі списку кандидатів ПІБ.
    Removes service tokens from a list of employee-name candidates.
    """

    cleaned: list[str] = []
    for value in values:
        stripped = value.strip()
        if not stripped or is_employee_query_stop_word(stripped):
            continue
        cleaned.append(stripped)
    return tuple(cleaned)


def sanitize_employee_query(value: str | None) -> str | None:
    """Прибирає дієслова та предмети ЗІЗ з employee_query.
    Strips command verbs and PPE item tokens from employee_query.
    """

    if not value or not value.strip():
        return None

    if is_employee_query_stop_word(value):
        return None

    tokens = value.strip().split()
    cleaned: list[str] = []
    for token in tokens:
        bare = token.strip(" ,;:")
        lowered = bare.lower()
        if is_command_verb_token(lowered):
            continue
        if _PPE_NOISE_TOKEN_PATTERN.fullmatch(bare):
            continue
        if is_training_noise_token(bare):
            break
        cleaned.append(bare)

    if not cleaned:
        return None
    return " ".join(cleaned)
