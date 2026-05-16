from pathlib import Path

from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.domain.entities.employee_readiness_level import EmployeeReadinessLevel
from osah.domain.entities.employee_work_readiness import EmployeeWorkReadiness
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.training_knowledge_check_result import TrainingKnowledgeCheckResult
from osah.domain.entities.training_status import TrainingStatus


# ###### ГОТОВНІСТЬ ПРАЦІВНИКА ДО РОБІТ / LOAD EMPLOYEE WORK READINESS ######
def load_employee_work_readiness(database_path: Path, employee_personnel_number: str) -> EmployeeWorkReadiness:
    """Повертає стислий стан готовності працівника для UI наряду-допуску.
    Returns a compact employee readiness snapshot for the work-permit UI.
    """

    trainings = tuple(
        record
        for record in load_training_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    medicals = tuple(
        record
        for record in load_medical_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )
    ppe_records = tuple(
        record
        for record in load_ppe_registry(database_path)
        if record.employee_personnel_number == employee_personnel_number
    )

    training_level, training_message = _resolve_training_readiness(trainings)
    medical_level, medical_message = _resolve_medical_readiness(medicals)
    ppe_level, ppe_message = _resolve_ppe_readiness(ppe_records)
    return EmployeeWorkReadiness(
        employee_personnel_number=employee_personnel_number,
        training_level=training_level,
        training_message=training_message,
        medical_level=medical_level,
        medical_message=medical_message,
        ppe_level=ppe_level,
        ppe_message=ppe_message,
    )


def _resolve_training_readiness(
    trainings: tuple,
) -> tuple[EmployeeReadinessLevel, str]:
    if not trainings:
        return EmployeeReadinessLevel.UNKNOWN, "Записи інструктажів відсутні."
    if any(record.knowledge_check_result == TrainingKnowledgeCheckResult.UNSATISFACTORY for record in trainings):
        return EmployeeReadinessLevel.CRITICAL, "Є незадовільна перевірка знань."
    if any(record.status == TrainingStatus.INVALID for record in trainings):
        return EmployeeReadinessLevel.CRITICAL, "Є конфлікт дат у хронології інструктажів."
    if any(record.status in {TrainingStatus.OVERDUE, TrainingStatus.MISSING} for record in trainings):
        return EmployeeReadinessLevel.CRITICAL, "Є прострочений або відсутній обов'язковий інструктаж."
    if any(record.status == TrainingStatus.WARNING for record in trainings):
        return EmployeeReadinessLevel.WARNING, "Наближається строк повторного інструктажу."
    return EmployeeReadinessLevel.NORMAL, "Критичних проблем не виявлено."


def _resolve_medical_readiness(
    medicals: tuple,
) -> tuple[EmployeeReadinessLevel, str]:
    if not medicals:
        return EmployeeReadinessLevel.UNKNOWN, "Записи меддопуску відсутні."
    if any(record.status in {MedicalStatus.EXPIRED, MedicalStatus.NOT_FIT} for record in medicals):
        return EmployeeReadinessLevel.CRITICAL, "Меддопуск прострочено або робота заборонена."
    if any(record.status in {MedicalStatus.WARNING, MedicalStatus.RESTRICTED} for record in medicals):
        return EmployeeReadinessLevel.WARNING, "Є обмеження або наближається строк медогляду."
    return EmployeeReadinessLevel.NORMAL, "Меддопуск чинний."


def _resolve_ppe_readiness(
    ppe_records: tuple,
) -> tuple[EmployeeReadinessLevel, str]:
    if not ppe_records:
        return EmployeeReadinessLevel.UNKNOWN, "Записи ЗІЗ відсутні."
    if any(record.status in {PpeStatus.EXPIRED, PpeStatus.NOT_ISSUED} for record in ppe_records):
        return EmployeeReadinessLevel.CRITICAL, "Є прострочений або невиданий обов'язковий ЗІЗ."
    if any(record.status == PpeStatus.WARNING for record in ppe_records):
        return EmployeeReadinessLevel.WARNING, "Наближається строк заміни ЗІЗ."
    if any(record.compliance_check_state == PpeComplianceCheckState.NOT_CHECKED for record in ppe_records):
        return EmployeeReadinessLevel.WARNING, "Не підтверджено відповідність ЗІЗ умовам роботи."
    return EmployeeReadinessLevel.NORMAL, "Проблем із забезпеченням ЗІЗ не виявлено."
