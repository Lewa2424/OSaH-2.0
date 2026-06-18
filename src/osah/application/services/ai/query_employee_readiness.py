from dataclasses import dataclass
from pathlib import Path

from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.application.services.load_employee_work_readiness import (
    is_employee_ready_for_work,
    load_employee_work_readiness,
)


@dataclass(slots=True, frozen=True)
class EmployeeReadinessQueryResult:
    """Результат запиту готовності працівника.
    Result of an employee readiness query.
    """

    employee_name: str
    personnel_number: str
    overall_ready: bool
    training_message: str
    medical_message: str
    ppe_message: str


def query_employee_readiness(
    database_path: Path,
    *,
    employee_query: str | None = None,
    personnel_number: str | None = None,
) -> EmployeeReadinessQueryResult | None:
    """Повертає стислий стан готовності працівника.
    Returns a compact employee readiness snapshot.
    """

    resolved_number = (personnel_number or "").strip()
    employee_name = ""

    if not resolved_number and employee_query:
        matches = search_employees_by_query(database_path, employee_query)
        if len(matches) != 1:
            return None
        resolved_number = matches[0].personnel_number
        employee_name = matches[0].full_name

    if not resolved_number:
        return None

    readiness = load_employee_work_readiness(database_path, resolved_number)
    if not employee_name:
        matches = search_employees_by_query(database_path, resolved_number)
        employee_name = matches[0].full_name if matches else resolved_number

    overall_ready = is_employee_ready_for_work(database_path, resolved_number)
    return EmployeeReadinessQueryResult(
        employee_name=employee_name,
        personnel_number=resolved_number,
        overall_ready=overall_ready,
        training_message=readiness.training_message,
        medical_message=readiness.medical_message,
        ppe_message=readiness.ppe_message,
    )
