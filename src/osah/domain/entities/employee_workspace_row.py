from dataclasses import dataclass

from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_module_status_summary import EmployeeModuleStatusSummary
from osah.domain.entities.employee_problem import EmployeeProblem
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.training_record import TrainingRecord


@dataclass(slots=True)
class EmployeeWorkspaceRow:
    """Рядок робочого простору працівників із готовими статусами для UI.
    Employee workspace row with precomputed statuses for UI.
    """

    employee: Employee
    status_level: EmployeeStatusLevel
    status_label: str
    status_reason: str
    department_name: str
    site_name: str
    position_name: str
    photo_path: str | None
    training_records: tuple[TrainingRecord, ...]
    ppe_records: tuple[PpeRecord, ...]
    medical_records: tuple[MedicalRecord, ...]
    module_summaries: tuple[EmployeeModuleStatusSummary, ...]
    problems: tuple[EmployeeProblem, ...]
