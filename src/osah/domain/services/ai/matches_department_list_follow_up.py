import re

_DEPARTMENT_LIST_FOLLOW_UP_PATTERN = re.compile(
    r"^\s*(?:"
    r"(?:(?:а|и)\s+)?(?:у\s+)?(?:них|їх|им|ім|їм|этим|цим|тим)"
    r"|"
    r"(?:(?:дай|покажи|показати|выведи|виведи|видай|выдай)\s+)?"
    r"(?:список\s+)?(?:сотрудник\w*|працівник\w*|работник\w*)"
    r"(?:\s+подразделени\w*|\s+підрозділ\w*)?"
    r")\s*$",
    re.IGNORECASE,
)


def matches_department_list_follow_up(raw_command: str) -> bool:
    """Перевіряє коротке уточнення «список сотрудников» після питання про підрозділ.
    Checks a short list-employees follow-up after a department question.
    """

    return bool(_DEPARTMENT_LIST_FOLLOW_UP_PATTERN.match(raw_command.strip()))
