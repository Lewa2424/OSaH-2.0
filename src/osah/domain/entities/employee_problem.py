from dataclasses import dataclass

from osah.domain.entities.employee_status_level import EmployeeStatusLevel


@dataclass(slots=True)
class EmployeeProblem:
    """Окрема причина проблемного або попереджувального стану працівника.
    A single reason behind an employee warning or blocking status.
    """

    module_name: str
    level: EmployeeStatusLevel
    title: str
    detail: str
    target_key: str
