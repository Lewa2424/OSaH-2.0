from dataclasses import dataclass

from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType


@dataclass(slots=True)
class TrainingRecord:
    """Запис інструктажу працівника.
    Запись инструктажа сотрудника.
    """

    record_id: int | None
    employee_personnel_number: str
    employee_full_name: str
    training_type: TrainingType
    event_date: str
    next_control_date: str
    conducted_by: str
    note_text: str
    status: TrainingStatus
