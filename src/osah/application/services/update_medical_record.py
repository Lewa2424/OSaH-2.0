from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.serialize_medical_record_for_audit import serialize_medical_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_medical_record_row import update_medical_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_medical_record_by_id import get_medical_record_by_id


# ###### ОНОВЛЕННЯ МЕДИЧНОГО ЗАПИСУ / UPDATE MEDICAL RECORD ######
def update_medical_record(
    database_path: Path,
    record_id: int,
    employee_personnel_number: str,
    valid_from_text: str,
    valid_until_text: str,
    medical_decision: str,
    restriction_note: str,
) -> None:
    """Оновлює медичний запис, синхронізує сповіщення і пише audit.
    Updates a medical record, synchronizes notifications and writes audit.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_decision = medical_decision.strip()
    normalized_restriction = restriction_note.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_decision:
        raise ValueError("Потрібно вибрати медичне рішення.")

    valid_from = parse_ui_date_text(valid_from_text)
    valid_until = parse_ui_date_text(valid_until_text)
    if valid_until < valid_from:
        raise ValueError("Дата завершення не може бути раніше дати початку.")

    connection = create_database_connection(database_path)
    try:
        previous_record = get_medical_record_by_id(connection, record_id)
        if previous_record is None:
            raise ValueError("Медичний запис не знайдено.")

        updated_record = MedicalRecord(
            record_id=record_id,
            employee_personnel_number=normalized_personnel_number,
            employee_full_name=previous_record.employee_full_name,
            valid_from=valid_from.isoformat(),
            valid_until=valid_until.isoformat(),
            medical_decision=MedicalDecision(normalized_decision),
            restriction_note=normalized_restriction,
            status=MedicalStatus.CURRENT,
        )
        update_medical_record_row(connection, updated_record)
        insert_audit_log(
            connection,
            event_type="medical.updated",
            module_name="medical",
            event_level="info",
            actor_name="system",
            entity_name=f"medical:{record_id}",
            result_status="success",
            description_text=(
                f"old=({serialize_medical_record_for_audit(previous_record)}) "
                f"new=({serialize_medical_record_for_audit(updated_record)})"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
