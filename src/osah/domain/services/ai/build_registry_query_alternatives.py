from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.parse_employee_name_query import parse_employee_name_query


def build_registry_query_alternatives(
    primary_query: str,
    raw_command: str | None = None,
) -> tuple[str, ...]:
    """Будує варіанти запиту: primary, фрагменти з raw_command, лише прізвище.
    Builds query alternatives: primary, raw_command fragments, surname-only.
    """

    alternatives: list[str] = []
    seen: set[str] = set()

    def add_alternative(value: str | None) -> None:
        normalized = (value or "").strip()
        if not normalized:
            return
        key = normalized.lower()
        if key in seen:
            return
        seen.add(key)
        alternatives.append(normalized)

    add_alternative(primary_query)

    parsed_primary = parse_employee_name_query(primary_query)
    if parsed_primary.surname and (parsed_primary.free_text or parsed_primary.first_initial):
        add_alternative(parsed_primary.surname)

    if raw_command:
        extracted = extract_employee_query_from_command(raw_command)
        if extracted:
            add_alternative(extracted)
            parsed_extracted = parse_employee_name_query(extracted)
            if parsed_extracted.surname and (
                parsed_extracted.free_text or parsed_extracted.first_initial
            ):
                add_alternative(parsed_extracted.surname)

    return tuple(alternatives)
