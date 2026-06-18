import re

_DEPARTMENT_READINESS_FOLLOW_UP_PATTERN = re.compile(
    r"^\s*(?:готовност\w*|готов\w*)"
    r"(?:\s+у\s+(?:них|них))?"
    r"\s*[?.!]?\s*$",
    re.IGNORECASE,
)


def matches_department_readiness_follow_up(raw_command: str) -> bool:
    """Перевіряє follow-up «готовность» після питання про підрозділ.
    Checks a readiness follow-up after a department question.
    """

    return bool(_DEPARTMENT_READINESS_FOLLOW_UP_PATTERN.match(raw_command.strip()))
