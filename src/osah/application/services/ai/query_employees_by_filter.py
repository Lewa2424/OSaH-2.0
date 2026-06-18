from dataclasses import dataclass
from pathlib import Path

from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.application.services.load_employee_registry import load_employee_registry
from osah.domain.entities.employee_status_level import EmployeeStatusLevel


@dataclass(slots=True, frozen=True)
class EmployeeFilterRow:
    """Працівник у результаті фільтра AI.
    Employee row in an AI filter result.
    """

    personnel_number: str
    full_name: str
    position_name: str
    department_name: str
    employment_status: str


def query_employees_by_filter(database_path: Path, filter_key: str | None) -> tuple[EmployeeFilterRow, ...]:
    """Повертає працівників за простим фільтром.
    Returns employees matching a simple filter key.
    """

    normalized = (filter_key or "active").strip().lower()
    if normalized in {"warning", "внимание", "увага"}:
        return _query_employees_by_workspace_status(database_path, EmployeeStatusLevel.WARNING)
    if normalized in {"critical", "критично", "критичний", "критический"}:
        return _query_employees_by_workspace_status(database_path, EmployeeStatusLevel.CRITICAL)
    if normalized in {"restricted", "обмеження", "обмежений", "ограничение"}:
        return _query_employees_by_workspace_status(database_path, EmployeeStatusLevel.RESTRICTED)

    rows: list[EmployeeFilterRow] = []
    for employee in load_employee_registry(database_path):
        if normalized in {"active", "активн", "активные"}:
            if employee.employment_status.strip().lower() not in {"active", "активний"}:
                continue
        elif normalized in {"terminated", "звільнен", "уволен", "уволенные"}:
            if employee.employment_status.strip().lower() not in {"terminated", "звільнений", "уволен"}:
                continue
        elif normalized in {"without_position", "без посади", "без должности"}:
            if employee.position_name.strip():
                continue
        elif normalized in {"without_department", "без дільниці", "без участка"}:
            if employee.department_name.strip():
                continue
        elif normalized in {"slinger", "стропальник", "стропальщик"}:
            if "строп" not in employee.position_name.lower():
                continue
        elif normalized in {"docker", "докер"}:
            if "док" not in employee.position_name.lower():
                continue
        else:
            continue
        rows.append(
            EmployeeFilterRow(
                personnel_number=employee.personnel_number,
                full_name=employee.full_name,
                position_name=employee.position_name,
                department_name=employee.department_name,
                employment_status=employee.employment_status,
            )
        )
    return tuple(sorted(rows, key=lambda row: row.full_name.lower()))


def _query_employees_by_workspace_status(
    database_path: Path,
    status_level: EmployeeStatusLevel,
) -> tuple[EmployeeFilterRow, ...]:
    rows: list[EmployeeFilterRow] = []
    for row in load_employee_workspace(database_path).rows:
        if row.status_level != status_level:
            continue
        rows.append(
            EmployeeFilterRow(
                personnel_number=row.employee.personnel_number,
                full_name=row.employee.full_name,
                position_name=row.position_name,
                department_name=row.department_name,
                employment_status=row.status_label,
            )
        )
    return tuple(sorted(rows, key=lambda item: item.full_name.lower()))
