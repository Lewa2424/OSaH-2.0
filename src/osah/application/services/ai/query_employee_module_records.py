from dataclasses import dataclass
from pathlib import Path

from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.domain.services.format_training_type_label import format_training_type_label


@dataclass(slots=True, frozen=True)
class EmployeeModuleRecordRow:
    """Короткий рядок запису працівника в модулі.
    Compact employee module record row.
    """

    title: str
    status_label: str
    detail: str


def query_employee_module_records(
    database_path: Path,
    *,
    employee_query: str | None = None,
    personnel_number: str | None = None,
    module_key: str | None = None,
) -> tuple[EmployeeModuleRecordRow, ...]:
    """Повертає записи працівника у вказаному модулі.
    Returns employee records for the requested module.
    """

    resolved_number = (personnel_number or "").strip()
    if not resolved_number and employee_query:
        matches = search_employees_by_query(database_path, employee_query)
        if len(matches) != 1:
            return ()
        resolved_number = matches[0].personnel_number

    if not resolved_number:
        return ()

    normalized_module = (module_key or "all").strip().lower()
    rows: list[EmployeeModuleRecordRow] = []

    if normalized_module in {"all", "ppe", "зіз", "сиз"}:
        for record in load_ppe_registry(database_path):
            if record.employee_personnel_number != resolved_number:
                continue
            rows.append(
                EmployeeModuleRecordRow(
                    title=record.ppe_name,
                    status_label=record.status.value,
                    detail=f"видача {record.issue_date}, заміна {record.replacement_date}",
                )
            )

    if normalized_module in {"all", "trainings", "інструктаж", "инструктаж"}:
        for record in load_training_registry(database_path):
            if record.employee_personnel_number != resolved_number:
                continue
            rows.append(
                EmployeeModuleRecordRow(
                    title=format_training_type_label(record.training_type),
                    status_label=record.status.value,
                    detail=f"дата {record.event_date}, наступний контроль {record.next_control_date or '—'}",
                )
            )

    if normalized_module in {"all", "medical", "мед"}:
        for record in load_medical_registry(database_path):
            if record.employee_personnel_number != resolved_number:
                continue
            rows.append(
                EmployeeModuleRecordRow(
                    title="Медогляд",
                    status_label=record.status.value,
                    detail=f"{record.valid_from} — {record.valid_until}, рішення {record.medical_decision.value}",
                )
            )

    return tuple(rows)
