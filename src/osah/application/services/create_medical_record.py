from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_exam_basis import MedicalExamBasis
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.parse_service_date_text import parse_service_date_text
from osah.domain.services.serialize_medical_record_for_audit import serialize_medical_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_medical_record import insert_medical_record
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СОЗДАНИЕ МЕДИЦИНСКОЙ ЗАПИСИ / CREATE MEDICAL RECORD ######
def create_medical_record(
    database_path: Path,
    employee_personnel_number: str,
    valid_from_text: str,
    valid_until_text: str,
    medical_decision: str,
    restriction_note: str,
    medical_exam_basis: str = "legacy_not_tracked",
    basis_text: str = "",
    basis_note: str = "",
    *,
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> None:
    """Создаёт новую медицинскую запись и синхронизирует контрольные уведомления.
    Creates a new medical record and synchronizes control notifications.
    """

    ensure_write_access(access_role, "create_medical_record")
    normalized_personnel_number = employee_personnel_number.strip()
    normalized_medical_decision = medical_decision.strip()
    normalized_restriction_note = restriction_note.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_medical_decision:
        raise ValueError("Потрібно вибрати медичне рішення.")

    valid_from = parse_service_date_text(valid_from_text)
    valid_until = parse_service_date_text(valid_until_text)
    if valid_until < valid_from:
        raise ValueError("Дата завершення не може бути раніше дати початку.")

    connection = create_database_connection(database_path)
    try:
        record = MedicalRecord(
            record_id=None,
            employee_personnel_number=normalized_personnel_number,
            employee_full_name="",
            valid_from=valid_from.isoformat(),
            valid_until=valid_until.isoformat(),
            medical_decision=MedicalDecision(normalized_medical_decision),
            restriction_note=normalized_restriction_note,
            status=MedicalStatus.CURRENT,
            medical_exam_basis=MedicalExamBasis(medical_exam_basis.strip() or "legacy_not_tracked"),
            basis_text=basis_text.strip(),
            basis_note=basis_note.strip(),
        )
        insert_medical_record(connection, record)
        insert_audit_log(
            connection,
            event_type="medical.created",
            module_name="medical",
            event_level="info",
            actor_name="system",
            entity_name=f"medical:{normalized_personnel_number}",
            result_status="success",
            description_text=f"created=({serialize_medical_record_for_audit(record)})",
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
