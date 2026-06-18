from osah.domain.entities.employee import Employee
from osah.domain.services.ai.expand_name_token_search_variants import expand_name_token_search_variants
from osah.domain.services.ai.normalize_cyrillic_search_text import normalize_cyrillic_search_text
from osah.domain.services.ai.normalize_person_name_token import normalize_person_name_token
from osah.domain.services.ai.parse_employee_name_query import (
    EmployeeNameQuery,
    expand_surname_search_variants,
    parse_employee_name_query,
)


def employee_matches_name_query(employee: Employee, query: EmployeeNameQuery) -> bool:
    """Перевіряє, чи працівник відповідає запиту за ПІБ/ініціалами.
    Checks whether an employee matches a parsed name query.
    """

    name_parts = employee.full_name.split()
    if not name_parts:
        return False

    surname = name_parts[0]
    first_name = name_parts[1] if len(name_parts) > 1 else ""
    patronymic = name_parts[2] if len(name_parts) > 2 else ""

    if query.free_text:
        return _free_text_matches_employee_name(query.free_text, employee.full_name)

    if query.surname:
        surname_variants = expand_surname_search_variants(query.surname)
        normalized_employee_surname = normalize_cyrillic_search_text(surname)
        if not any(
            normalize_cyrillic_search_text(variant) == normalized_employee_surname
            or normalized_employee_surname.startswith(normalize_cyrillic_search_text(variant))
            or normalize_cyrillic_search_text(variant).startswith(normalized_employee_surname)
            for variant in surname_variants
        ):
            return False

    if query.first_initial:
        if not first_name:
            return False
        if normalize_cyrillic_search_text(first_name)[0] != normalize_cyrillic_search_text(query.first_initial)[0]:
            return False

    if query.patronymic_initial:
        if not patronymic:
            return False
        if normalize_cyrillic_search_text(patronymic)[0] != normalize_cyrillic_search_text(query.patronymic_initial)[0]:
            return False

    return bool(query.surname or query.free_text)


def _employee_matches_surname_and_first_initial(employee: Employee, query: EmployeeNameQuery) -> bool:
    if not query.surname or not query.first_initial:
        return False
    return employee_matches_name_query(
        employee,
        EmployeeNameQuery(
            surname=query.surname,
            first_initial=query.first_initial,
        ),
    )


def match_employees_by_name_query(
    employees: tuple[Employee, ...],
    query_text: str,
) -> tuple[Employee, ...]:
    """Повертає працівників, що відповідають фрагменту ПІБ або ініціалам.
    Returns employees that match a name fragment or initials query.
    """

    parsed_query = parse_employee_name_query(query_text)
    if not parsed_query.surname and not parsed_query.free_text:
        return ()

    strict_matches = tuple(
        employee for employee in employees if employee_matches_name_query(employee, parsed_query)
    )
    if strict_matches or not parsed_query.patronymic_initial:
        return strict_matches

    relaxed_matches = tuple(
        employee
        for employee in employees
        if _employee_matches_surname_and_first_initial(employee, parsed_query)
    )
    if len(relaxed_matches) == 1:
        return relaxed_matches
    return ()


def _free_text_matches_employee_name(query_text: str, full_name: str) -> bool:
    query_tokens = query_text.split()
    name_tokens = full_name.split()
    if not query_tokens or not name_tokens:
        return False

    if not _name_tokens_equivalent(query_tokens[0], name_tokens[0]):
        return False

    if len(query_tokens) == 1:
        return True

    remaining_name = name_tokens[1:]
    for query_token in query_tokens[1:]:
        if not remaining_name:
            return False
        matched_index = _find_matching_name_token_index(query_token, remaining_name)
        if matched_index is None:
            return False
        remaining_name = remaining_name[matched_index + 1 :]
    return True


def _find_matching_name_token_index(query_token: str, name_tokens: list[str]) -> int | None:
    for index, name_token in enumerate(name_tokens):
        if _name_tokens_equivalent(query_token, name_token):
            return index
    return None


def _name_tokens_equivalent(query_token: str, name_token: str) -> bool:
    if normalize_person_name_token(query_token) == normalize_person_name_token(name_token):
        return True
    normalized_query = normalize_cyrillic_search_text(query_token)
    normalized_name = normalize_cyrillic_search_text(name_token)
    if normalized_query == normalized_name:
        return True
    if normalized_query and normalized_name and normalized_query[0] == normalized_name[0]:
        if len(normalized_query) == 1 or len(normalized_name) == 1:
            return True
    for variant in expand_name_token_search_variants(query_token):
        variant_normalized = normalize_cyrillic_search_text(variant)
        if variant_normalized == normalized_name:
            return True
        if normalized_name.startswith(variant_normalized) or variant_normalized.startswith(normalized_name):
            return True
    return False
