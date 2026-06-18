from dataclasses import dataclass
from pathlib import Path

from osah.application.services.ai.query_employees_by_department import query_employees_by_department
from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.ai.match_position_name_query import position_name_matches_query


@dataclass(slots=True, frozen=True)
class MissingPpeEmployeeRow:
    """Працівник без потрібного ЗІЗ.
    Employee missing the requested PPE item.
    """

    personnel_number: str
    full_name: str
    ppe_name: str
    status: PpeStatus


def query_employees_missing_ppe(
    database_path: Path,
    ppe_item_query: str,
    *,
    department_query: str | None = None,
    position_query: str | None = None,
) -> tuple[MissingPpeEmployeeRow, ...]:
    """Повертає працівників без виданого або простроченого ЗІЗ.
    Returns employees missing or overdue for the requested PPE item.
    """

    candidates = search_ppe_catalog_candidates(database_path, ppe_item_query)
    if not candidates:
        return ()

    resolved_name = candidates[0]
    candidate_names = {name.lower() for name in candidates}
    allowed_numbers = _allowed_personnel_numbers(
        database_path,
        department_query=department_query,
        position_query=position_query,
    )
    rows: list[MissingPpeEmployeeRow] = []
    seen_employees: set[str] = set()

    for record in load_ppe_registry(database_path):
        if record.ppe_name.strip().lower() not in candidate_names:
            continue
        if record.status not in {PpeStatus.NOT_ISSUED, PpeStatus.EXPIRED}:
            continue
        employee_key = record.employee_personnel_number
        if employee_key in seen_employees:
            continue
        if allowed_numbers is not None and employee_key not in allowed_numbers:
            continue
        seen_employees.add(employee_key)
        rows.append(
            MissingPpeEmployeeRow(
                personnel_number=record.employee_personnel_number,
                full_name=record.employee_full_name,
                ppe_name=resolved_name,
                status=record.status,
            )
        )

    return tuple(sorted(rows, key=lambda row: row.full_name.lower()))


def resolve_missing_ppe_item_label(database_path: Path, ppe_item_query: str) -> str:
    """Повертає підпис предмета ЗІЗ для відповіді AI.
    Returns the PPE item label used in AI answers.
    """

    candidates = search_ppe_catalog_candidates(database_path, ppe_item_query)
    return candidates[0] if candidates else ppe_item_query.strip()


def _allowed_personnel_numbers(
    database_path: Path,
    *,
    department_query: str | None,
    position_query: str | None,
) -> frozenset[str] | None:
    department = (department_query or "").strip()
    position = (position_query or "").strip()
    if not department and not position:
        return None

    allowed: set[str] | None = None

    if department:
        department_numbers = {
            row.personnel_number for row in query_employees_by_department(database_path, department)
        }
        allowed = department_numbers

    if position:
        position_numbers = frozenset(
            employee.personnel_number
            for employee in load_employee_registry(database_path)
            if position_name_matches_query(employee.position_name, position)
        )
        allowed = position_numbers if allowed is None else allowed & set(position_numbers)

    return frozenset(allowed or ())
