import re
from dataclasses import dataclass

from osah.domain.services.ai.normalize_cyrillic_search_text import normalize_cyrillic_search_text

_INITIALS_PATTERN = re.compile(
    r"^(.+?)\s+([а-яіїєґa-z])\.?\s*([а-яіїєґa-z])\.?$",
    re.IGNORECASE,
)
_SINGLE_INITIAL_PATTERN = re.compile(
    r"^(.+?)\s+([а-яіїєґa-z])\.?$",
    re.IGNORECASE,
)
_FULL_NAME_PATTERN = re.compile(
    r"^([А-ЯІЇЄҐA-Z][а-яіїєґa-z'`-]+)"
    r"(?:\s+([А-ЯІЇЄҐA-Z][а-яіїєґa-z'`-]+))?"
    r"(?:\s+([А-ЯІЇЄҐA-Z][а-яіїєґa-z'`-]+))?$",
    re.IGNORECASE,
)


@dataclass(slots=True, frozen=True)
class EmployeeNameQuery:
    """Розібраний запит на пошук працівника за ПІБ.
    Parsed employee lookup query by full name.
    """

    surname: str | None = None
    first_initial: str | None = None
    patronymic_initial: str | None = None
    free_text: str | None = None


def parse_employee_name_query(query_text: str) -> EmployeeNameQuery:
    """Розбирає фрагмент ПІБ, ініціали або вільний текст.
    Parses a name fragment, initials or free-text employee query.
    """

    normalized = " ".join(query_text.strip().split())
    if not normalized:
        return EmployeeNameQuery()

    initials_match = _INITIALS_PATTERN.match(normalized)
    if initials_match is not None:
        return EmployeeNameQuery(
            surname=initials_match.group(1).strip(),
            first_initial=initials_match.group(2).strip(),
            patronymic_initial=initials_match.group(3).strip(),
        )

    single_initial_match = _SINGLE_INITIAL_PATTERN.match(normalized)
    if single_initial_match is not None:
        return EmployeeNameQuery(
            surname=single_initial_match.group(1).strip(),
            first_initial=single_initial_match.group(2).strip(),
        )

    full_name_match = _FULL_NAME_PATTERN.match(normalized)
    if full_name_match is not None and full_name_match.group(2):
        return EmployeeNameQuery(
            surname=full_name_match.group(1).strip(),
            free_text=normalized,
        )

    parts = normalized.split()
    if len(parts) == 1:
        return EmployeeNameQuery(surname=parts[0])

    return EmployeeNameQuery(free_text=normalized)


def expand_surname_search_variants(surname: str) -> tuple[str, ...]:
    """Повертає варіанти прізвища з урахуванням дательного відмінка.
    Returns surname variants including common dative-case forms.
    """

    cleaned = surname.strip()
    if not cleaned:
        return ()

    variants: set[str] = {cleaned, normalize_cyrillic_search_text(cleaned)}
    if cleaned.endswith("у"):
        stem = cleaned[:-1]
        variants.add(stem)
        variants.add(normalize_cyrillic_search_text(stem))
        if stem.endswith("к") or stem.endswith("н"):
            with_o = f"{stem}о"
            variants.add(with_o)
            variants.add(normalize_cyrillic_search_text(with_o))
    if cleaned.endswith("ю"):
        stem = cleaned[:-1]
        variants.add(stem)
        variants.add(f"{stem}я")
        variants.add(normalize_cyrillic_search_text(stem))
        variants.add(normalize_cyrillic_search_text(f"{stem}я"))

    return tuple(value for value in variants if value)
