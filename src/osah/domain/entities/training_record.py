from dataclasses import dataclass

from osah.domain.entities.training_knowledge_check_result import TrainingKnowledgeCheckResult
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_admission_status import TrainingWorkAdmissionStatus
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
    person_category: TrainingPersonCategory = TrainingPersonCategory.OWN_EMPLOYEE
    requires_primary_on_workplace: bool = False
    work_risk_category: TrainingWorkRiskCategory = TrainingWorkRiskCategory.NOT_APPLICABLE
    next_control_basis: TrainingNextControlBasis = TrainingNextControlBasis.MANUAL
    knowledge_check_result: TrainingKnowledgeCheckResult = TrainingKnowledgeCheckResult.LEGACY_NOT_TRACKED
    work_admission_status: TrainingWorkAdmissionStatus = TrainingWorkAdmissionStatus.LEGACY_NOT_TRACKED
    knowledge_check_note: str = ""
    basis_text: str = ""
    basis_note: str = ""
    is_current: bool = True
    archived_at: str | None = None
    archive_reason: str = ""
    replaced_by_record_id: int | None = None
    source_module: str = ""
    source_record_id: int | None = None
    source_key: str = ""
