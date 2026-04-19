from dataclasses import dataclass

from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_status import MedicalStatus


@dataclass(slots=True)
class MedicalRecord:
    """Запис меддопуску та обмежень працівника.
    Запись меддопуска и ограничений сотрудника.
    """

    record_id: int | None
    employee_personnel_number: str
    employee_full_name: str
    valid_from: str
    valid_until: str
    medical_decision: MedicalDecision
    restriction_note: str
    status: MedicalStatus
