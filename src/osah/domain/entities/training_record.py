from dataclasses import dataclass

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory


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
    work_risk_category: TrainingWorkRiskCategory = TrainingWorkRiskCategory.NOT_APPLICABLE
    next_control_basis: TrainingNextControlBasis = TrainingNextControlBasis.MANUAL
