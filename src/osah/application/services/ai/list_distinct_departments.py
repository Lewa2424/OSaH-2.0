from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry


def list_distinct_departments(database_path: Path) -> tuple[str, ...]:
    """Повертає унікальні назви підрозділів із реєстру працівників.
    Returns distinct department names from the employee registry.
    """

    names: set[str] = set()
    for employee in load_employee_registry(database_path):
        department_name = employee.department_name.strip()
        if department_name:
            names.add(department_name)
    return tuple(sorted(names, key=str.lower))
