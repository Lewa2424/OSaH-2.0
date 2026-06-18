from pathlib import Path

from osah.domain.entities.employee import Employee
from osah.domain.services.ai.match_employees_by_name_query import match_employees_by_name_query
from osah.domain.services.ai.normalize_cyrillic_search_text import normalize_cyrillic_search_text
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employees import list_employees


def search_employees_by_query(database_path: Path, query_text: str) -> tuple[Employee, ...]:
    """Шукає працівників за фрагментом ПІБ, ініціалами або табельним номером.
    Searches employees by name fragment, initials or personnel number.
    """

    normalized_query = query_text.strip()
    if not normalized_query:
        return ()

    connection = create_database_connection(database_path)
    try:
        employees = tuple(list_employees(connection))
    finally:
        connection.close()

    lowered_query = normalized_query.lower()
    if lowered_query.isdigit():
        exact_number_matches = tuple(
            employee
            for employee in employees
            if employee.personnel_number.lower() == lowered_query
            or employee.personnel_number.lstrip("0") == lowered_query.lstrip("0")
        )
        if exact_number_matches:
            return exact_number_matches

    exact_number_matches = tuple(
        employee
        for employee in employees
        if employee.personnel_number.lower() == lowered_query
        or employee.personnel_number.lstrip("0") == lowered_query.lstrip("0")
    )
    if exact_number_matches:
        return exact_number_matches

    name_matches = match_employees_by_name_query(employees, normalized_query)
    if name_matches:
        return name_matches

    normalized_free_text = normalize_cyrillic_search_text(normalized_query)
    return tuple(
        employee
        for employee in employees
        if normalized_free_text in normalize_cyrillic_search_text(employee.full_name)
        or normalized_free_text in employee.personnel_number.lower()
    )
