import re

_EMPLOYEE_PROBLEMS_QUERY_PATTERN = re.compile(
    r"(?:"
    r"які|какие|якие|що|что|як|готов\w*|потрібн\w*|нужн\w*"
    r")\b.{0,24}проблем\w*.{0,12}(?:\bу|\bв)\s+",
    re.IGNORECASE,
)


def matches_employee_problems_query(raw_command: str) -> bool:
    """Перевіряє запит про проблеми конкретного працівника.
    Checks whether the phrase asks for a specific employee's problems.
    """

    return bool(_EMPLOYEE_PROBLEMS_QUERY_PATTERN.search(raw_command.strip()))
