import re

from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.extract_short_name_follow_up import extract_short_name_follow_up

_WRITE_VERB_NAMES_PATTERN = re.compile(
    r"(?:занеси|занести|видай|выдай|выдать|дай|раздай|впиши|выпиши|оформи|проведи|провести)\s+"
    r"(?:каск\w*|черевик\w*|ботинк\w*|рукавиц\w*|перчат\w*|роб\w*|спецодяг\w*|обув\w*\s+)?"
    r"(?:сотрудник[уа]?|работник[уа]?|працівник[уа]?)?\s*"
    r"(?P<names>.+?)"
    r"(?:\s+(?:сегодня|сьогодні|сегодняшн\w*|today)\b.*)?$"
    ,
    re.IGNORECASE,
)


def extract_employee_queries_from_command(raw_command: str) -> tuple[str, ...]:
    """Витягує один або кілька фрагментів ПІБ із команди.
    Extracts one or more employee name fragments from a command.
    """

    short_name = extract_short_name_follow_up(raw_command)
    if short_name is not None:
        return (short_name,)

    multi_names = _extract_names_from_write_command(raw_command)
    if multi_names:
        return multi_names

    single_query = extract_employee_query_from_command(raw_command)
    if single_query is None:
        return ()

    parts = _split_employee_queries(single_query)
    if parts:
        return parts
    return (single_query,)


def _extract_names_from_write_command(raw_command: str) -> tuple[str, ...]:
    match = _WRITE_VERB_NAMES_PATTERN.search(raw_command.strip())
    if match is None:
        return ()
    names_blob = match.group("names").strip().rstrip("?.!,")
    return _split_employee_queries(names_blob)


def _split_employee_queries(employee_query: str) -> tuple[str, ...]:
    normalized = employee_query.replace(" та ", ",").replace(" і ", ",").replace(" и ", ",")
    parts = [part.strip() for part in normalized.split(",") if part.strip()]
    if len(parts) <= 1:
        if re.search(r"\s+(?:и|і|та)\s+", employee_query, re.IGNORECASE):
            split_parts = re.split(r"\s+(?:и|і|та)\s+", employee_query, flags=re.IGNORECASE)
            cleaned = tuple(part.strip() for part in split_parts if part.strip())
            if len(cleaned) > 1:
                return cleaned
        return ()
    return tuple(parts)
