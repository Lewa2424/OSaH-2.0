from dataclasses import dataclass
from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.domain.services.ai.match_department_name_query import department_name_matches_query


@dataclass(slots=True, frozen=True)
class DepartmentEmployeeRow:
    """Працівник підрозділу в результаті AI-запиту.
    Employee row in a department AI query result.
    """

    personnel_number: str
    full_name: str
    position_name: str
    department_name: str
    employment_status: str


def query_employees_by_department(
    database_path: Path,
    department_query: str,
) -> tuple[DepartmentEmployeeRow, ...]:
    """Повертає активних працівників підрозділу за фрагментом назви.
    Returns active employees in a department matching the query fragment.
    """

    rows: list[DepartmentEmployeeRow] = []
    for employee in load_employee_registry(database_path):
        if employee.employment_status.strip().lower() not in {"active", "активний"}:
            continue
        if not department_name_matches_query(employee.department_name, department_query):
            continue
        rows.append(
            DepartmentEmployeeRow(
                personnel_number=employee.personnel_number,
                full_name=employee.full_name,
                position_name=employee.position_name,
                department_name=employee.department_name,
                employment_status=employee.employment_status,
            )
        )
    return tuple(sorted(rows, key=lambda row: row.full_name.lower()))
