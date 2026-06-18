from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.update_employee import update_employee
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_employee_field_updates import AiEmployeeFieldUpdates


def update_employee_fields_batch(
    database_path: Path,
    employee_personnel_numbers: tuple[str, ...],
    field_updates: AiEmployeeFieldUpdates,
    *,
    access_role: AccessRole,
) -> int:
    """Оновлює поля кількох працівників за одним сценарієм.
    Updates fields for multiple employees using one scenario.
    """

    ensure_write_access(access_role, "update_employee_fields_batch")
    normalized_numbers = tuple(number.strip() for number in employee_personnel_numbers if number.strip())
    if not normalized_numbers:
        raise ValueError("Потрібно вибрати хоча б одного працівника.")
    if not any((field_updates.position_name, field_updates.department_name, field_updates.employment_status)):
        raise ValueError("Потрібно вказати поле для оновлення.")

    employees_by_number = {
        employee.personnel_number: employee for employee in load_employee_registry(database_path)
    }
    updated_count = 0
    for personnel_number in normalized_numbers:
        employee = employees_by_number.get(personnel_number)
        if employee is None:
            raise ValueError(f"Працівника {personnel_number} не знайдено.")
        update_employee(
            database_path,
            personnel_number=personnel_number,
            full_name=employee.full_name,
            department_name=field_updates.department_name or employee.department_name,
            position_name=field_updates.position_name or employee.position_name,
            employment_status=field_updates.employment_status or employee.employment_status,
            access_role=access_role,
        )
        updated_count += 1
    return updated_count
