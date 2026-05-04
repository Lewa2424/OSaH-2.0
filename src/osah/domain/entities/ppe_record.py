from dataclasses import dataclass

from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_status import PpeStatus


@dataclass(slots=True)
class PpeRecord:
    """Запис по засобу індивідуального захисту.
    Запись по средству индивидуальной защиты.
    """

    record_id: int | None
    employee_personnel_number: str
    employee_full_name: str
    ppe_name: str
    is_required: bool
    is_issued: bool
    issue_date: str
    replacement_date: str
    quantity: int
    note_text: str
    status: PpeStatus
    provision_status: PpeProvisionStatus = PpeProvisionStatus.LEGACY_NOT_TRACKED
    compliance_check_state: PpeComplianceCheckState = PpeComplianceCheckState.LEGACY_NOT_TRACKED
    basis_text: str = ""
    basis_note: str = ""
