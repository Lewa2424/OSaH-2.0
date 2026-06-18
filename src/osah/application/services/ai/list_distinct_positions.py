from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry


def list_distinct_positions(database_path: Path) -> tuple[str, ...]:
    """Повертає унікальні назви посад із реєстру працівників.
    Returns distinct position names from the employee registry.
    """

    names: set[str] = set()
    for employee in load_employee_registry(database_path):
        position_name = employee.position_name.strip()
        if position_name:
            names.add(position_name)
    return tuple(sorted(names, key=str.lower))
