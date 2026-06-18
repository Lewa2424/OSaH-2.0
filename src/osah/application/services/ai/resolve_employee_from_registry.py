from pathlib import Path

from osah.domain.entities.employee import Employee
from osah.domain.entities.registry_entity_resolution import RegistryEntityResolution
from osah.domain.services.ai.build_registry_query_alternatives import build_registry_query_alternatives
from osah.domain.services.ai.employee_name_matches_query import employee_name_matches_query
from osah.domain.services.ai.match_employees_by_name_query import match_employees_by_name_query
from osah.domain.services.ai.suggest_registry_name_candidates import suggest_registry_name_candidates
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employees import list_employees


def resolve_employee_from_registry(
    database_path: Path,
    employee_query: str,
    *,
    raw_command: str | None = None,
    suggestion_limit: int = 5,
    suggestion_min_score: float = 0.35,
) -> RegistryEntityResolution:
    """Зіставляє фрагмент ПІБ з реєстром працівників і пропонує близькі варіанти.
    Matches an employee name fragment against the registry and suggests close alternatives.
    """

    normalized_query = employee_query.strip()
    if not normalized_query:
        return RegistryEntityResolution(status="empty")

    connection = create_database_connection(database_path)
    try:
        employees = tuple(list_employees(connection))
    finally:
        connection.close()

    if normalized_query.isdigit():
        exact_matches = _employees_by_personnel_number(employees, normalized_query)
        if len(exact_matches) == 1:
            employee = exact_matches[0]
            return RegistryEntityResolution(
                status="resolved",
                canonical_name=employee.full_name,
                resolved_personnel_number=employee.personnel_number,
            )
        if len(exact_matches) > 1:
            return _ambiguous_resolution(exact_matches)

    alternatives = build_registry_query_alternatives(normalized_query, raw_command)
    for alternative in alternatives:
        resolution = _resolve_by_name_matches(employees, alternative)
        if resolution is not None:
            return resolution

    registry_names = tuple(employee.full_name for employee in employees)
    suggestions = suggest_registry_name_candidates(
        normalized_query,
        registry_names,
        exact_match_checker=employee_name_matches_query,
        limit=suggestion_limit,
        min_score=suggestion_min_score,
    )
    if suggestions:
        return RegistryEntityResolution(status="suggest", candidates=suggestions)
    return RegistryEntityResolution(status="not_found")


def _resolve_by_name_matches(
    employees: tuple[Employee, ...],
    query: str,
) -> RegistryEntityResolution | None:
    matches = match_employees_by_name_query(employees, query)
    if not matches:
        return None
    if len(matches) == 1:
        employee = matches[0]
        return RegistryEntityResolution(
            status="resolved",
            canonical_name=employee.full_name,
            resolved_personnel_number=employee.personnel_number,
        )
    return _ambiguous_resolution(matches)


def _ambiguous_resolution(matches: tuple[Employee, ...]) -> RegistryEntityResolution:
    return RegistryEntityResolution(
        status="ambiguous",
        candidates=tuple(employee.full_name for employee in matches[:10]),
    )


def _employees_by_personnel_number(
    employees: tuple[Employee, ...],
    personnel_number: str,
) -> tuple[Employee, ...]:
    lowered = personnel_number.lower()
    return tuple(
        employee
        for employee in employees
        if employee.personnel_number.lower() == lowered
        or employee.personnel_number.lstrip("0") == lowered.lstrip("0")
    )
