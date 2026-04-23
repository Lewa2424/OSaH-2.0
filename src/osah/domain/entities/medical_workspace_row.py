from dataclasses import dataclass

from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_status import MedicalStatus


@dataclass(slots=True)
class MedicalWorkspaceRow:
    """Рядок Qt-реєстру меддопусків із причиною статусу.
    Qt medical registry row with status reason.
    """

    record_id: int | None
    employee_personnel_number: str
    employee_full_name: str
    department_name: str
    site_name: str
    position_name: str
    valid_from: str
    valid_until: str
    medical_decision: MedicalDecision
    decision_label: str
    restriction_note: str
    has_restriction: bool
    status: MedicalStatus
    status_label: str
    status_reason: str
