import re

_DEPARTMENT_PROBLEMS_FOLLOW_UP_PATTERN = re.compile(
    r"^\s*(?:(?:какие|які|якие)\s+)?(?:проблем\w*|критич\w*)"
    r"(?:\s+у\s+(?:них|них|них))?"
    r"\s*[?.!]?\s*$",
    re.IGNORECASE,
)


def matches_department_problems_follow_up(raw_command: str) -> bool:
    """Перевіряє follow-up «какие проблемы» після питання про підрозділ.
    Checks a problems follow-up after a department question.
    """

    return bool(_DEPARTMENT_PROBLEMS_FOLLOW_UP_PATTERN.match(raw_command.strip()))
