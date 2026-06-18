from osah.domain.entities.employee import Employee
from osah.domain.services.ai.match_employees_by_name_query import match_employees_by_name_query


def employee_name_matches_query(employee_full_name: str, query: str) -> bool:
    """Перевіряє, чи повне ПІБ працівника відповідає фрагменту запиту.
    Checks whether an employee full name matches a query fragment.
    """

    normalized_name = employee_full_name.strip()
    normalized_query = query.strip()
    if not normalized_name or not normalized_query:
        return False

    probe = Employee(
        personnel_number="",
        full_name=normalized_name,
        position_name="",
        department_name="",
        employment_status="active",
    )
    return bool(match_employees_by_name_query((probe,), normalized_query))
