from dataclasses import dataclass
from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry_rows import load_training_registry_rows
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.services.ai.normalize_ai_module_key import normalize_ai_module_key
from osah.domain.services.format_medical_decision_label import format_medical_decision_label


@dataclass(slots=True, frozen=True)
class ModuleStatusEmployeeRow:
    """Працівник із відповідним статусом у модулі.
    Employee matching the requested module status.
    """

    personnel_number: str
    full_name: str
    department_name: str
    position_name: str
    status_label: str
    detail: str


def query_employees_by_module_status(
    database_path: Path,
    *,
    module_key: str | None,
    filter_key: str | None,
) -> tuple[ModuleStatusEmployeeRow, ...]:
    """Повертає працівників із заданим статусом у модулі.
    Returns employees with the requested status in the given module.
    """

    normalized_module = normalize_ai_module_key(module_key)
    normalized_filter = (filter_key or "").strip().lower()
    if normalized_module in {"all"} or not normalized_filter:
        return ()

    employees_by_number = {
        employee.personnel_number: employee for employee in load_employee_registry(database_path)
    }

    if normalized_module in {"trainings", "інструктаж", "инструктаж"}:
        return _query_training_rows(database_path, normalized_filter, employees_by_number)
    if normalized_module in {"ppe", "зіз", "сиз"}:
        return _query_ppe_rows(database_path, normalized_filter, employees_by_number)
    if normalized_module in {"medical", "мед"}:
        return _query_medical_rows(database_path, normalized_filter, employees_by_number)
    return ()


def _query_training_rows(
    database_path: Path,
    filter_key: str,
    employees_by_number: dict,
) -> tuple[ModuleStatusEmployeeRow, ...]:
    registry_filter = _training_registry_filter(filter_key)
    if registry_filter is None:
        return ()

    rows = load_training_registry_rows(database_path, registry_filter)
    seen: set[str] = set()
    result: list[ModuleStatusEmployeeRow] = []
    for row in rows:
        if row.employee_personnel_number in seen:
            continue
        seen.add(row.employee_personnel_number)
        employee = employees_by_number.get(row.employee_personnel_number)
        result.append(
            ModuleStatusEmployeeRow(
                personnel_number=row.employee_personnel_number,
                full_name=row.employee_full_name,
                department_name=employee.department_name if employee is not None else "",
                position_name=employee.position_name if employee is not None else "",
                status_label=row.status_label,
                detail=f"{row.training_type_label}, наступний контроль {row.next_control_date_label}",
            )
        )
    return tuple(sorted(result, key=lambda item: item.full_name.lower()))


def _query_ppe_rows(
    database_path: Path,
    filter_key: str,
    employees_by_number: dict,
) -> tuple[ModuleStatusEmployeeRow, ...]:
    statuses = _ppe_statuses(filter_key)
    if not statuses:
        return ()

    seen: set[str] = set()
    result: list[ModuleStatusEmployeeRow] = []
    for record in load_ppe_registry(database_path):
        if record.status not in statuses:
            continue
        if record.employee_personnel_number in seen:
            continue
        seen.add(record.employee_personnel_number)
        employee = employees_by_number.get(record.employee_personnel_number)
        result.append(
            ModuleStatusEmployeeRow(
                personnel_number=record.employee_personnel_number,
                full_name=record.employee_full_name,
                department_name=employee.department_name if employee is not None else "",
                position_name=employee.position_name if employee is not None else "",
                status_label=_ppe_status_label(record.status),
                detail=record.ppe_name,
            )
        )
    return tuple(sorted(result, key=lambda item: item.full_name.lower()))


def _query_medical_rows(
    database_path: Path,
    filter_key: str,
    employees_by_number: dict,
) -> tuple[ModuleStatusEmployeeRow, ...]:
    statuses = _medical_statuses(filter_key)
    if not statuses:
        return ()

    seen: set[str] = set()
    result: list[ModuleStatusEmployeeRow] = []
    for record in load_medical_registry(database_path):
        if record.status not in statuses:
            continue
        if record.employee_personnel_number in seen:
            continue
        seen.add(record.employee_personnel_number)
        employee = employees_by_number.get(record.employee_personnel_number)
        result.append(
            ModuleStatusEmployeeRow(
                personnel_number=record.employee_personnel_number,
                full_name=record.employee_full_name,
                department_name=employee.department_name if employee is not None else "",
                position_name=employee.position_name if employee is not None else "",
                status_label=_medical_status_label(record.status),
                detail=_build_medical_detail(record),
            )
        )
    return tuple(sorted(result, key=lambda item: item.full_name.lower()))


def _training_registry_filter(filter_key: str) -> TrainingRegistryFilter | None:
    mapping = {
        "warning": TrainingRegistryFilter.WARNING,
        "overdue": TrainingRegistryFilter.OVERDUE,
        "missing": TrainingRegistryFilter.MISSING,
        "critical": TrainingRegistryFilter.OVERDUE,
    }
    return mapping.get(filter_key)


def _ppe_statuses(filter_key: str) -> frozenset[PpeStatus]:
    mapping: dict[str, frozenset[PpeStatus]] = {
        "warning": frozenset({PpeStatus.WARNING}),
        "overdue": frozenset({PpeStatus.EXPIRED}),
        "not_issued": frozenset({PpeStatus.NOT_ISSUED}),
        "critical": frozenset({PpeStatus.EXPIRED, PpeStatus.NOT_ISSUED}),
    }
    return mapping.get(filter_key, frozenset())


def _medical_statuses(filter_key: str) -> frozenset[MedicalStatus]:
    mapping: dict[str, frozenset[MedicalStatus]] = {
        "warning": frozenset({MedicalStatus.WARNING}),
        "overdue": frozenset({MedicalStatus.EXPIRED}),
        "restricted": frozenset({MedicalStatus.RESTRICTED, MedicalStatus.NOT_FIT}),
        "critical": frozenset({MedicalStatus.EXPIRED, MedicalStatus.NOT_FIT}),
    }
    return mapping.get(filter_key, frozenset())


def _ppe_status_label(status: PpeStatus) -> str:
    labels = {
        PpeStatus.WARNING: "увага",
        PpeStatus.EXPIRED: "прострочено",
        PpeStatus.NOT_ISSUED: "не видано",
        PpeStatus.CURRENT: "актуально",
    }
    return labels.get(status, status.value)


def _medical_status_label(status: MedicalStatus) -> str:
    labels = {
        MedicalStatus.WARNING: "увага",
        MedicalStatus.EXPIRED: "прострочено",
        MedicalStatus.RESTRICTED: "обмеження",
        MedicalStatus.NOT_FIT: "не допущено",
        MedicalStatus.CURRENT: "актуально",
    }
    return labels.get(status, status.value)


def _build_medical_detail(record) -> str:
    decision_label = format_medical_decision_label(record.medical_decision)
    restriction_note = (record.restriction_note or "").strip()
    if restriction_note:
        return f"{decision_label}; {restriction_note}"
    return decision_label
