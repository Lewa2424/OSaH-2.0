from dataclasses import dataclass
from pathlib import Path

from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.ai.normalize_ai_module_key import normalize_ai_module_key


@dataclass(slots=True, frozen=True)
class OverdueSummaryQueryResult:
    """Агреговані прострочення по модулях.
    Aggregated overdue counts by module.
    """

    ppe_expired: int
    ppe_not_issued: int
    ppe_warning: int
    training_overdue: int
    training_warning: int
    medical_expired: int
    medical_warning: int
    work_permit_expired: int
    work_permit_warning: int


def query_overdue_summary(database_path: Path, module_key: str | None = None) -> OverdueSummaryQueryResult:
    """Повертає кількість прострочень і попереджень у реєстрах.
    Returns overdue and warning counts across registries.
    """

    normalized_key = normalize_ai_module_key(module_key)
    include_ppe = normalized_key in {"all", "ppe", "зіз", "сиз"}
    include_trainings = normalized_key in {"all", "trainings", "інструктаж", "инструктаж"}
    include_medical = normalized_key in {"all", "medical", "мед"}
    include_work_permits = normalized_key in {"all", "work_permits", "наряд", "наряди"}

    ppe_expired = 0
    ppe_not_issued = 0
    ppe_warning = 0
    if include_ppe:
        for record in load_ppe_registry(database_path):
            if record.status == PpeStatus.EXPIRED:
                ppe_expired += 1
            elif record.status == PpeStatus.NOT_ISSUED:
                ppe_not_issued += 1
            elif record.status == PpeStatus.WARNING:
                ppe_warning += 1

    training_overdue = 0
    training_warning = 0
    if include_trainings:
        for record in load_training_registry(database_path):
            if record.status == TrainingStatus.OVERDUE:
                training_overdue += 1
            elif record.status == TrainingStatus.WARNING:
                training_warning += 1

    medical_expired = 0
    medical_warning = 0
    if include_medical:
        for record in load_medical_registry(database_path):
            if record.status == MedicalStatus.EXPIRED:
                medical_expired += 1
            elif record.status == MedicalStatus.WARNING:
                medical_warning += 1

    work_permit_expired = 0
    work_permit_warning = 0
    if include_work_permits:
        for record in load_work_permit_registry(database_path):
            if record.status == WorkPermitStatus.EXPIRED:
                work_permit_expired += 1
            elif record.status == WorkPermitStatus.WARNING:
                work_permit_warning += 1

    return OverdueSummaryQueryResult(
        ppe_expired=ppe_expired,
        ppe_not_issued=ppe_not_issued,
        ppe_warning=ppe_warning,
        training_overdue=training_overdue,
        training_warning=training_warning,
        medical_expired=medical_expired,
        medical_warning=medical_warning,
        work_permit_expired=work_permit_expired,
        work_permit_warning=work_permit_warning,
    )
