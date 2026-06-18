import re

from osah.domain.services.ai.command_verb_tokens import is_training_noise_token, sanitize_employee_query

_EMPLOYEE_FOR_PATTERN = re.compile(
    r"(?:для|for)\s+([А-Яа-яІіЇїЄєҐґA-Za-z][А-Яа-яІіЇїЄєҐґA-Za-z\.\s]{1,60})",
    re.IGNORECASE,
)
_PERSONNEL_IN_COMMAND_PATTERN = re.compile(
    r"(?:працівник[уа]?|работник[уа]?|сотрудник[уа]?|таб\.?\s*№?)\s*(\d{1,6})\b",
    re.IGNORECASE,
)
_PPE_ONLY_PREFIX = (
    r"(?:каск\w*|черевик\w*|ботинк\w*|рукавиц\w*|перчат\w*|"
    r"жилет\w*|комбінезон\w*|взутт\w*|обув\w*)"
)
_PERSON_NAME_TOKEN = (
    r"(?!(?:первичн|повторн|первинн|цільов|целев|инструктаж|інструктаж)\w*)"
    r"[А-Яа-яІіЇїЄєҐґ][а-яіїєґ'`-]+"
)
_EMPLOYEE_ROLE_PREFIX = r"(?:сотрудник[уа]?|работник[уа]?|працівник[уа]?)\s+"
_EMPLOYEE_AFTER_ITEM_PATTERN = re.compile(
    rf"{_PPE_ONLY_PREFIX}\s+"
    rf"(?:{_EMPLOYEE_ROLE_PREFIX})?"
    r"([А-Яа-яІіЇїЄєҐґ][А-Яа-яІіЇїЄєҐґ'`-]+(?:\s+[А-Яа-яІіЇїЄєҐґ][а-яіїєґ'`-]+){0,2})"
    r"(?:\s+((?:[А-ЯA-ZІЇЄҐ]\.\s*){1,2}[А-ЯA-ZІЇЄҐ]\.))?",
    re.IGNORECASE,
)
_EMPLOYEE_DATIVE_PATTERN = re.compile(
    r"\b([А-Яа-яІіЇїЄєҐґ][а-яіїєґ'`-]{2,30}(?:у|ю))"
    r"(?:\s+((?:[А-ЯA-ZІЇЄҐ]\.\s*){1,2}[А-ЯA-ZІЇЄҐ]\.?))?"
    r"(?=\s*$|\s*[,.!?])",
    re.IGNORECASE,
)
_EMPLOYEE_AT_PATTERN = re.compile(
    r"(?:проблем\w*|готов\w*|потрібн\w*|нужн\w*|стан\w*).{0,12}(?:\bу|\bв)\s+"
    r"([А-Яа-яІіЇїЄєҐґ][А-Яа-яІіЇїЄєҐґ'`.-]{1,25}(?:\s+[А-Яа-яІіЇїЄєҐґ][а-яіїєґ'`.-]{1,25})?)",
    re.IGNORECASE,
)
_WRITE_NAME_OR_INITIALS = (
    rf"({_PERSON_NAME_TOKEN}"
    rf"(?:\s+(?:"
    rf"{_PERSON_NAME_TOKEN}(?:\s+{_PERSON_NAME_TOKEN})?"
    r"|(?:[А-ЯA-ZІЇЄҐ]\.\s*){1,2}[А-ЯA-ZІЇЄҐ]\.?"
    r"))?)"
)
_WRITE_EMPLOYEE_PATTERN = re.compile(
    r"(?:занеси|занести|внеси|внести|проведи|провести|оформи|"
    r"выдай|видай|дай|раздай|впиши|выпиши|"
    r"продли|продлить|продовж|подовж)\s+"
    rf"(?:{_PPE_ONLY_PREFIX}\s+)?"
    rf"(?:{_EMPLOYEE_ROLE_PREFIX})?"
    rf"({_WRITE_NAME_OR_INITIALS})"
    r"(?=\s+(?:повторн|первичн|первинн|цільов|целев|инструктаж|інструктаж|"
    r"мед(?:допуск)?|медичн|медкоміс|сегодня|сьогодні)|\s*$|[,.])",
    re.IGNORECASE,
)


def extract_personnel_number_from_command(raw_command: str) -> str | None:
    """Витягує табельний номер із фрази на кшталт «работнику 0030».
    Extracts a personnel number from phrases like 'employee 0030'.
    """

    match = _PERSONNEL_IN_COMMAND_PATTERN.search(raw_command)
    if match is None:
        return None
    return match.group(1).strip()


def extract_employee_query_from_command(raw_command: str) -> str | None:
    """Витягує фрагмент ПІБ або табельний номер із тексту команди.
    Extracts an employee name fragment or personnel number from command text.
    """

    personnel_number = extract_personnel_number_from_command(raw_command)
    if personnel_number is not None:
        return personnel_number

    for_match = _EMPLOYEE_FOR_PATTERN.search(raw_command)
    if for_match is not None:
        return _finalize_employee_query(_clean_captured_name(for_match.group(1)))

    item_match = _EMPLOYEE_AFTER_ITEM_PATTERN.search(raw_command)
    if item_match is not None:
        return _finalize_employee_query(_join_name_and_initials(item_match.group(1), item_match.group(2)))

    write_match = _WRITE_EMPLOYEE_PATTERN.search(raw_command)
    if write_match is not None:
        captured = write_match.group(1).strip()
        initials_match = re.search(
            r"((?:[А-ЯA-ZІЇЄҐ]\.\s*){1,2}[А-ЯA-ZІЇЄҐ]\.?)$",
            captured,
            re.IGNORECASE,
        )
        if initials_match is not None and initials_match.start() > 0:
            name_part = captured[: initials_match.start()].strip()
            return _finalize_employee_query(
                _join_name_and_initials(name_part, initials_match.group(1))
            )
        return _finalize_employee_query(_clean_captured_name(captured))

    dative_match = _EMPLOYEE_DATIVE_PATTERN.search(raw_command)
    if dative_match is not None:
        return _finalize_employee_query(_join_name_and_initials(dative_match.group(1), dative_match.group(2)))

    at_match = _EMPLOYEE_AT_PATTERN.search(raw_command)
    if at_match is not None:
        return _finalize_employee_query(_clean_captured_name(at_match.group(1)))

    return None


def _finalize_employee_query(value: str | None) -> str | None:
    return sanitize_employee_query(value)


def _join_name_and_initials(name: str, initials: str | None) -> str:
    cleaned_name = _clean_captured_name(name)
    cleaned_initials = _normalize_initials_block((initials or "").strip())
    if cleaned_initials:
        return f"{cleaned_name} {cleaned_initials}".strip()
    return cleaned_name


def _normalize_initials_block(initials: str) -> str:
    letters = re.findall(r"[А-ЯA-ZІЇЄҐ]", initials, re.IGNORECASE)
    if len(letters) >= 2:
        return f"{letters[0].upper()}.{letters[1].upper()}."
    if len(letters) == 1:
        return f"{letters[0].upper()}."
    return initials


def _clean_captured_name(value: str) -> str:
    captured = value.strip()
    if re.search(r"[А-Яа-яA-Za-zІіЇїЄєҐґ]\.[А-Яа-яA-Za-zІіЇЄҐґ]\.$", captured):
        return captured
    if re.search(r"\b[А-ЯA-ZІЇЄҐ]\.[А-ЯA-ZІЇЄҐ]\.$", captured):
        return captured
    captured = re.split(
        r"\s+(?:"
        r"сьогодні|сегодня|today|сегодняшн\w*|вчора|вчера|"
        r"текущ\w*|первичн\w*|повторн\w*|первинн\w*|цільов\w*|целев\w*|"
        r"инструктаж\w*|інструктаж\w*|"
        r"ограничен\w*|обмежен\w*|restriction"
        r")\b",
        captured,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    captured = re.split(
        r"\s+за\s+(?:сегодня|сьогодні|today|сегодняшн\w*)",
        captured,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    tokens = captured.split()
    trimmed_tokens: list[str] = []
    for token in tokens:
        if is_training_noise_token(token):
            break
        trimmed_tokens.append(token)
    captured = " ".join(trimmed_tokens)
    if re.search(r"\b[А-ЯA-ZІЇЄҐ]\.[А-ЯA-ZІЇЄҐ]\.?$", captured):
        return captured
    return captured.rstrip(".,!?") or captured
