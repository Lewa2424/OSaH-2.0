from dataclasses import dataclass


@dataclass(slots=True)
class EmployeeTopbarSummary:
    """Коротка кадрова сводка для верхней панели.
    Compact employee summary for the top command bar.
    """

    active_employee_count: int
    department_count: int
    new_employee_count: int
    archived_employee_count: int
