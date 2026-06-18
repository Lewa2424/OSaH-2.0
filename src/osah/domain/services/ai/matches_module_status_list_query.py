import re

from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.matches_employee_problems_query import matches_employee_problems_query
from osah.domain.services.ai.normalize_ai_status_filter_key import detect_status_filter_key_from_command

_LIST_LEAD_PATTERN = re.compile(
    r"(?:^|\s)(?:у\s+кого|кому|хто|які\s+працівник|какие\s+сотрудник)\b",
    re.IGNORECASE,
)
_SHOW_EMPLOYEES_PROBLEM_PATTERN = re.compile(
    r"(?:^|\s)(?:покажи|показати|показать|найди|виведи|выведи|вывести)\b"
    r".{0,40}(?:працівник|сотрудник|employees?)"
    r".{0,80}(?:проблемн|інструктаж|инструктаж|не\s+закрыт|не\s+закрит)",
    re.IGNORECASE,
)
_UNCLOSED_TRAINING_PATTERN = re.compile(
    r"(?:^|\s)(?:у\s+кого|кому|хто|кто)\b"
    r".{0,60}(?:не\s+закрыт\w*|не\s+закрит\w*)"
    r".{0,30}(?:інструктаж\w*|инструктаж\w*)",
    re.IGNORECASE,
)

_MODULE_PATTERN = re.compile(
    r"(?:"
    r"інструктаж\w*|инструктаж\w*|"
    r"зіз|сиз|ppe|спецодяг|"
    r"мед(?:огляд|осмотр)?\w*|"
    r"наряд\w*"
    r")",
    re.IGNORECASE,
)

_PPE_TOKEN_PATTERN = re.compile(
    r"\b(?:каск\w*|черевик\w*|ботинк\w*|рукавиц\w*|перчатк\w*|"
    r"жилет\w*|комбінезон\w*|каску|каски|взутт\w*|спецодяг\w*)\b",
    re.IGNORECASE,
)


_NON_PERSON_EMPLOYEE_FRAGMENTS = frozenset(
    {
        "статус",
        "status",
        "стан",
        "модуль",
        "розділ",
        "раздел",
        "увага",
        "внимание",
        "проблема",
        "проблемы",
        "сотрудников",
        "сотрудник",
        "сотрудникам",
        "працівників",
        "працівник",
        "работников",
        "работник",
    }
)


def matches_module_status_list_query(raw_command: str) -> bool:
    """Перевіряє запит списку працівників за статусом модуля.
    Checks whether the phrase asks for employees by module status.
    """

    text = raw_command.strip()
    if not text:
        return False
    if matches_employee_problems_query(text):
        return False
    if _has_personal_employee_target(text):
        return False
    if _PPE_TOKEN_PATTERN.search(text) and re.search(
        r"(?:не\s+)?(?:видали|выдали|потрібн|нужн)",
        text,
        re.IGNORECASE,
    ):
        return False
    if not _LIST_LEAD_PATTERN.search(text) and not _SHOW_EMPLOYEES_PROBLEM_PATTERN.search(text):
        if not _UNCLOSED_TRAINING_PATTERN.search(text):
            return False
    if not _MODULE_PATTERN.search(text):
        return False
    return detect_status_filter_key_from_command(text) is not None


def _has_personal_employee_target(text: str) -> bool:
    employee_query = extract_employee_query_from_command(text)
    if not employee_query:
        return False
    normalized = employee_query.strip().lower()
    return normalized not in _NON_PERSON_EMPLOYEE_FRAGMENTS
