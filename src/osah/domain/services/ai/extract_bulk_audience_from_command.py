import re

from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.services.ai.extract_bulk_department_span_from_command import (
    extract_bulk_department_span_from_command,
)
from osah.domain.services.ai.extract_bulk_position_span_from_command import (
    extract_bulk_position_span_from_command,
)

_DEPARTMENT_CAPTURE_PATTERN = re.compile(
    r"(?:"
    r"(?:працівникам|работникам|сотрудникам)\s+"
    r"(?:підрозділ[уа]?|подразделени[яе]?|отдел[уа]?|дільниц[іи]|участк[ае]|цех[уа]?|служб[аи])\s+"
    r"|"
    r"(?:підрозділ[уа]?|подразделени[яе]?|отдел[уа]?|дільниц[іи]|участк[ае]|цех[уа]?|служб[аи])\s+"
    r")"
    r"(.+?)"
    r"(?=\s+(?:"
    r"дополнительно|додатково|видай|выдай|занеси|занести|проведи|додай|добавь|"
    r"по\s+\d|по\s+пар|за\s+|сьогодні|сегодня|today|каск|перчатк|рукавиц|ботинк|інструктаж|инструктаж|мед"
    r")|$)",
    re.IGNORECASE,
)

_PERMIT_PARTICIPANTS_PATTERN = re.compile(
    r"(?:учасникам|участникам)\s+(?:наряду\s+)?№?\s*(\d+)",
    re.IGNORECASE,
)

_POSITION_PATTERN = re.compile(
    r"(?:"
    r"(?:всім|усім|всем|працівникам|работникам)\s+"
    r"(стропальник\w*|докер\w*|зварник\w*|сварщик\w*|комірник\w*|електромонтер\w*)"
    r"|"
    r"(?:всім|усім|всем)\s+([а-яіїєґa-z-]{4,30}(?:никам|ників|щикам|щиків|ам|ів))\b"
    r")",
    re.IGNORECASE,
)

_FILTER_SLINGER_PATTERN = re.compile(r"\b(?:стропальник\w*|стропальщик\w*)\b", re.IGNORECASE)
_FILTER_DOCKER_PATTERN = re.compile(r"\b(?:докер\w*)\b", re.IGNORECASE)

_BULK_MARKER_PATTERN = re.compile(
    r"(?:\b(?:всім|усім|всем|групі|группе|групою|пакетно|масово|массово|"
    r"для\s+всіх|для\s+всех|вибраним|выбранным|списком|списку)\b)",
    re.IGNORECASE,
)

_BULK_WRITE_VERB_PATTERN = re.compile(
    r"\b(?:"
    r"видай|выдай|выдать|занеси|занести|проведи|провести|"
    r"додай|добавь|масово|массово|пакетно|раздай|"
    r"оформи|впиши|выпиши|застосуй|примени"
    r")\b",
    re.IGNORECASE,
)

_AUDIENCE_MARKER_PATTERN = re.compile(
    r"(?:"
    r"учасникам\s+наряду|участникам\s+наряду|"
    r"працівникам\s+(?:підрозділ|дільниц|участк|цех|служб)|"
    r"работникам\s+(?:подразделени|отдел|участк|цех|служб)|"
    r"підрозділ[уа]?\s+|подразделени[яе]?\s+|"
    r"дільниц[іи]\s+|участк[уае]\s+|"
    r"в\s+должност|на\s+должност|в\s+цех|в\s+отдел|"
    r"всему\s+подраздел|всему\s+підрозділ"
    r")",
    re.IGNORECASE,
)

_DEPARTMENT_CONTEXT_PATTERN = re.compile(
    r"(?:"
    r"(?:підрозділ|подразделени|отдел|дільниц|участк|цех|служб)"
    r"|"
    r"(?:працівникам|работникам|сотрудникам)\s+"
    r"(?:підрозділ|подразделени|отдел|дільниц|участк|цех|служб)"
    r")",
    re.IGNORECASE,
)


def has_bulk_marker_in_command(raw_command: str) -> bool:
    """Перевіряє наявність маркера масової аудиторії у фразі.
    Checks whether the command text contains a bulk audience marker.
    """

    return bool(_BULK_MARKER_PATTERN.search(raw_command.strip()))


def extract_bulk_audience_from_command(raw_command: str) -> AiBulkAudienceSpec | None:
    """Витягує критерії bulk-аудиторії з тексту команди.
    Extracts bulk audience criteria from command text.
    """

    text = raw_command.strip()
    if not text:
        return None

    department_query = _extract_department_query(text)
    permit_number = _extract_permit_number(text)
    position_query = _extract_position_query(text)
    filter_key = _extract_filter_key(text)
    arrived_from, arrived_until = _extract_arrived_span(text)

    if not any((department_query, permit_number, position_query, filter_key, arrived_from, arrived_until)):
        return None

    return AiBulkAudienceSpec(
        department_query=department_query,
        position_query=position_query,
        filter_key=filter_key,
        permit_number=permit_number,
        arrived_from=arrived_from,
        arrived_until=arrived_until,
        combine_mode="and",
    )


def has_implicit_bulk_audience_marker(raw_command: str) -> bool:
    """Перевіряє, чи команда містить неявну групову аудиторію для write-bulk.
    Checks whether the command implies a bulk write audience (not read queries).
    """

    text = raw_command.strip()
    if not text:
        return False
    if has_bulk_marker_in_command(text):
        return True
    if not _BULK_WRITE_VERB_PATTERN.search(text):
        return False
    if _AUDIENCE_MARKER_PATTERN.search(text):
        return True
    spec = extract_bulk_audience_from_command(text)
    return spec is not None


def is_department_audience_in_command(raw_command: str, employee_query: str | None) -> bool:
    """Перевіряє, чи employee_query у контексті підрозділу, а не ПІБ.
    Checks whether employee_query refers to a department rather than a person.
    """

    if not employee_query or not employee_query.strip():
        return False
    if not _DEPARTMENT_CONTEXT_PATTERN.search(raw_command):
        return False
    query = re.escape(employee_query.strip())
    return bool(
        re.search(
            rf"(?:підрозділ|подразделени|отдел|дільниц|участк|цех|служб).{{0,40}}{query}",
            raw_command,
            re.IGNORECASE,
        )
        or re.search(
            rf"(?:працівникам|работникам|сотрудникам).{{0,60}}{query}",
            raw_command,
            re.IGNORECASE,
        )
    )


def _extract_department_query(text: str) -> str | None:
    span = extract_bulk_department_span_from_command(text)
    if span:
        return span
    match = _DEPARTMENT_CAPTURE_PATTERN.search(text)
    if match is None:
        return None
    return _clean_department_name(match.group(1))


def _extract_position_query(text: str) -> str | None:
    span = extract_bulk_position_span_from_command(text)
    if span:
        return span
    match = _POSITION_PATTERN.search(text)
    if match is None:
        return None
    for group in match.groups():
        if group and group.strip():
            return group.strip()
    return None


def _extract_permit_number(text: str) -> str | None:
    permit_match = _PERMIT_PARTICIPANTS_PATTERN.search(text)
    if permit_match:
        return permit_match.group(1).strip()
    generic_match = re.search(r"(?:наряд[уа]?|№)\s*(\d+)", text, re.IGNORECASE)
    if generic_match and re.search(r"(?:учасник|участник|наряд)", text, re.IGNORECASE):
        return generic_match.group(1).strip()
    return None


def _extract_filter_key(text: str) -> str | None:
    lowered = text.lower()
    if any(token in lowered for token in ("активн", "активные")):
        return "active"
    if _FILTER_SLINGER_PATTERN.search(text):
        return "slinger"
    if _FILTER_DOCKER_PATTERN.search(text):
        return "docker"
    return None


def _extract_arrived_span(text: str) -> tuple[str | None, str | None]:
    """Витягує діапазон дати прийому для аудиторії «новоприбулих».
    Extracts hire-date span for newly arrived employee audiences.
    """

    lowered = text.lower()
    if not any(token in lowered for token in ("новим", "новых", "новоприб", "нових", "прийнят", "принят")):
        return None, None
    if "тижден" in lowered or "недел" in lowered:
        return "current_week", None
    if "місяц" in lowered or "месяц" in lowered:
        return "current_month", None
    if "сьогодні" in lowered or "сегодня" in lowered:
        return "сьогодні", None
    return "current_week", None


def _clean_department_name(raw_name: str) -> str | None:
    cleaned = raw_name.strip(" ,.;:")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None
