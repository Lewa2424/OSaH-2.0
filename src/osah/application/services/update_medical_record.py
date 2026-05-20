from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_exam_basis import MedicalExamBasis
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.serialize_medical_record_for_audit import serialize_medical_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_medical_record_row import update_medical_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_medical_record_by_id import get_medical_record_by_id


# ###### ОБНОВЛЕНИЕ МЕДИЦИНСКОЙ ЗАПИСИ / UPDATE MEDICAL RECORD ######
def update_medical_record(
    database_path: Path,
    record_id: int,
    employee_personnel_number: str,
    valid_from_text: str,
    valid_until_text: str,
    medical_decision: str,
    restriction_note: str,
    medical_exam_basis: str = "legacy_not_tracked",
    basis_text: str = "",
    basis_note: str = "",
    *,
    access_role: AccessRole,
) -> None:
    """Обновляет медицинскую запись, синхронизирует уведомления и пишет audit.
    Updates a medical record, synchronizes notifications and writes audit.
    """

    ensure_write_access(access_role, "update_medical_record")
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
            medical_exam_basis=MedicalExamBasis(medical_exam_basis.strip() or "legacy_not_tracked"),
            basis_text=basis_text.strip(),
            basis_note=basis_note.strip(),
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
