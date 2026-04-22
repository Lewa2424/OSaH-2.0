from dataclasses import dataclass

from osah.domain.entities.employee_status_level import EmployeeStatusLevel


@dataclass(slots=True)
class EmployeeModuleStatusSummary:
    """Короткий стан одного ОП-модуля в картці працівника.
    Compact state of one safety module in an employee card.
    """

    module_name: str
    level: EmployeeStatusLevel
    label: str
    reason: str
