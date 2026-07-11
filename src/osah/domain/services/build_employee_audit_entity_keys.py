from osah.domain.entities.employee_audit_entity_keys import EmployeeAuditEntityKeys
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.work_permit_record import WorkPermitRecord


# ###### КЛЮЧІ AUDIT ДЛЯ ПРАЦІВНИКА / BUILD EMPLOYEE AUDIT ENTITY KEYS ######
def build_employee_audit_entity_keys(
    personnel_number: str,
    training_records: tuple[TrainingRecord, ...],
    ppe_records: tuple[PpeRecord, ...],
    medical_records: tuple[MedicalRecord, ...],
    work_permit_records: tuple[WorkPermitRecord, ...],
) -> EmployeeAuditEntityKeys:
    """Збирає exact-ключі та prefix для пошуку audit-подій працівника.
    Builds exact keys and prefix patterns for employee audit log lookup.
    """

    normalized_personnel_number = personnel_number.strip()
    exact_keys: set[str] = {
        f"employee:{normalized_personnel_number}",
        f"training:{normalized_personnel_number}",
        f"ppe:{normalized_personnel_number}",
        f"medical:{normalized_personnel_number}",
        normalized_personnel_number,
    }

    for training_record in training_records:
        if training_record.record_id is not None:
            exact_keys.add(f"training:{training_record.record_id}")

    for ppe_record in ppe_records:
        if ppe_record.record_id is not None:
            exact_keys.add(f"ppe:{ppe_record.record_id}")

    for medical_record in medical_records:
        if medical_record.record_id is not None:
            exact_keys.add(f"medical:{medical_record.record_id}")

    for work_permit_record in work_permit_records:
        permit_number = work_permit_record.permit_number.strip()
        if permit_number:
            exact_keys.add(f"work_permit:{permit_number}")

    return EmployeeAuditEntityKeys(
        exact_entity_names=frozenset(exact_keys),
        training_entity_prefix=f"training:{normalized_personnel_number}",
        legacy_personnel_entity_name=normalized_personnel_number,
    )
