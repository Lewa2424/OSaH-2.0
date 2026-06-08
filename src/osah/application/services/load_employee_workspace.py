from pathlib import Path

from osah.domain.entities.employee import Employee
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.domain.services.build_employee_workspace_row import build_employee_workspace_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


# ###### ЗАВАНТАЖЕННЯ РОБОЧОГО ПРОСТОРУ ПРАЦІВНИКІВ / LOAD EMPLOYEE WORKSPACE ######
def load_employee_workspace(database_path: Path) -> EmployeeWorkspace:
    """Завантажує реальні дані активних працівників і пов'язані ОП-статуси для Qt-екрана.
    Loads active employee data and related safety statuses for the Qt screen.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    enterprise_name = app_settings.get("enterprise.display_name", "").strip() or "Підприємство"

    all_employees = load_employee_registry(database_path)
    employees = tuple(e for e in all_employees if e.employment_status.lower() == "active")
    trainings = load_training_registry(database_path)
    ppe_records = load_ppe_registry(database_path)
    medical_records = load_medical_registry(database_path)
    work_permits = load_work_permit_registry(database_path)

    rows = tuple(
        build_employee_workspace_row(
            employee=_resolve_employee_photo_path(database_path, employee),
            training_records=(
                record for record in trainings if record.employee_personnel_number == employee.personnel_number
            ),
            ppe_records=(record for record in ppe_records if record.employee_personnel_number == employee.personnel_number),
            medical_records=(
                record for record in medical_records if record.employee_personnel_number == employee.personnel_number
            ),
            work_permit_records=(
                record
                for record in work_permits
                if any(
                    participant.employee_personnel_number == employee.personnel_number
                    for participant in record.participants
                )
            ),
        )
        for employee in employees
    )

    return EmployeeWorkspace(enterprise_name=enterprise_name, rows=rows)


def _resolve_employee_photo_path(database_path: Path, employee: Employee) -> Employee:
    photo_path = employee.photo_path.strip() if employee.photo_path else ""
    if photo_path:
        resolved_photo_path = Path(photo_path)
        if not resolved_photo_path.is_absolute():
            resolved_photo_path = database_path.parent / photo_path
        return employee.__class__(
            personnel_number=employee.personnel_number,
            full_name=employee.full_name,
            position_name=employee.position_name,
            department_name=employee.department_name,
            employment_status=employee.employment_status,
            photo_path=str(resolved_photo_path),
            created_at_text=employee.created_at_text,
        )
    return employee
