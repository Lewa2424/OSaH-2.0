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


def create_medical_records_batch(
    database_path: Path,
    employee_personnel_numbers: tuple[str, ...],
    valid_from_text: str,
    valid_until_text: str,
    medical_decision: str,
    restriction_note: str,
    *,
    access_role: AccessRole,
) -> int:
    """Створює медичні записи для кількох працівників в одній транзакції.
    Creates medical records for multiple employees in one transaction.
    """

    ensure_write_access(access_role, "create_medical_records_batch")
    normalized_numbers = tuple(number.strip() for number in employee_personnel_numbers if number.strip())
    normalized_decision = medical_decision.strip()
    normalized_restriction = restriction_note.strip()
    if not normalized_numbers:
        raise ValueError("Потрібно вибрати хоча б одного працівника.")
    if not normalized_decision:
        raise ValueError("Потрібно вибрати медичне рішення.")

    valid_from = parse_service_date_text(valid_from_text)
    valid_until = parse_service_date_text(valid_until_text)
    if valid_until < valid_from:
        raise ValueError("Дата закінчення не може бути раніше дати початку.")

    connection = create_database_connection(database_path)
    try:
        for personnel_number in normalized_numbers:
            record = MedicalRecord(
                record_id=None,
                employee_personnel_number=personnel_number,
                employee_full_name="",
                valid_from=valid_from.isoformat(),
                valid_until=valid_until.isoformat(),
                medical_decision=MedicalDecision(normalized_decision),
                restriction_note=normalized_restriction,
                status=MedicalStatus.CURRENT,
                medical_exam_basis=MedicalExamBasis.LEGACY_NOT_TRACKED,
            )
            insert_medical_record(connection, record)
            insert_audit_log(
                connection,
                event_type="medical.created",
                module_name="medical",
                event_level="info",
                actor_name="system",
                entity_name=f"medical:{personnel_number}",
                result_status="success",
                description_text=f"created=({serialize_medical_record_for_audit(record)})",
            )
        insert_audit_log(
            connection,
            event_type="medical.bulk_created",
            module_name="medical",
            event_level="info",
            actor_name="system",
            entity_name="medical:bulk",
            result_status="success",
            description_text=f"count={len(normalized_numbers)}",
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
    return len(normalized_numbers)
