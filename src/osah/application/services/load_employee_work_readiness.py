from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_work_readiness import EmployeeWorkReadiness
from osah.domain.entities.employee_readiness_level import EmployeeReadinessLevel
from osah.domain.services.build_employee_workspace_row import build_employee_workspace_row


def load_employee_work_readiness(database_path: Path, employee_personnel_number: str) -> EmployeeWorkReadiness:
    """Повертає стислий стан готовності працівника для UI наряду-допуску.
    Returns a compact employee readiness snapshot for the work-permit UI.
    """

    employee = _find_employee(database_path, employee_personnel_number)
    if employee is None:
        return EmployeeWorkReadiness(
            employee_personnel_number=employee_personnel_number,
            training_level=EmployeeReadinessLevel.UNKNOWN,
            training_message="Працівника не знайдено.",
            medical_level=EmployeeReadinessLevel.UNKNOWN,
            medical_message="Працівника не знайдено.",
            ppe_level=EmployeeReadinessLevel.UNKNOWN,
            ppe_message="Працівника не знайдено.",
        )

    training_records = tuple(
        record
        for record in load_training_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    medical_records = tuple(
        record
        for record in load_medical_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    ppe_records = tuple(
        record
        for record in load_ppe_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    work_permit_records = tuple(
        record
        for record in load_work_permit_registry(database_path)
        if any(
            participant.employee_personnel_number == employee_personnel_number
            for participant in record.participants
        )
    )

    workspace_row = build_employee_workspace_row(
        employee,
        training_records,
        ppe_records,
        medical_records,
        work_permit_records,
    )
    training_summary, ppe_summary, medical_summary, _ = workspace_row.module_summaries
    return EmployeeWorkReadiness(
        employee_personnel_number=employee_personnel_number,
        training_level=_map_status_level(training_summary.level),
        training_message=training_summary.reason,
        medical_level=_map_status_level(medical_summary.level),
        medical_message=medical_summary.reason,
        ppe_level=_map_status_level(ppe_summary.level),
        ppe_message=ppe_summary.reason,
    )


def is_employee_ready_for_work(database_path: Path, employee_personnel_number: str) -> bool:
    """Перевіряє, чи працівник має допуск до робіт за тією ж логікою, що картка.
    Checks whether the employee is work-ready using the same logic as the card.
    """

    employee = _find_employee(database_path, employee_personnel_number)
    if employee is None:
        return False

    training_records = tuple(
        record
        for record in load_training_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    medical_records = tuple(
        record
        for record in load_medical_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    ppe_records = tuple(
        record
        for record in load_ppe_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    work_permit_records = tuple(
        record
        for record in load_work_permit_registry(database_path)
        if any(
            participant.employee_personnel_number == employee_personnel_number
            for participant in record.participants
        )
    )
    workspace_row = build_employee_workspace_row(
        employee,
        training_records,
        ppe_records,
        medical_records,
        work_permit_records,
    )
    return workspace_row.status_level == EmployeeStatusLevel.NORMAL


def _find_employee(database_path: Path, employee_personnel_number: str) -> Employee | None:
    return next(
        (employee for employee in load_employee_registry(database_path) if employee.personnel_number == employee_personnel_number),
        None,
    )


def _map_status_level(status_level: EmployeeStatusLevel) -> EmployeeReadinessLevel:
    if status_level == EmployeeStatusLevel.CRITICAL:
        return EmployeeReadinessLevel.CRITICAL
    if status_level == EmployeeStatusLevel.WARNING:
        return EmployeeReadinessLevel.WARNING
    if status_level == EmployeeStatusLevel.ARCHIVED:
        return EmployeeReadinessLevel.UNKNOWN
    return EmployeeReadinessLevel.NORMAL
