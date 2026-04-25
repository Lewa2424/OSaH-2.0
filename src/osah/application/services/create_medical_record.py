from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.infrastructure.database.commands.insert_medical_record import insert_medical_record
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СТВОРЕННЯ МЕДИЧНОГО ЗАПИСУ / CREATE MEDICAL RECORD ######
def create_medical_record(
    database_path: Path,
    employee_personnel_number: str,
    valid_from_text: str,
    valid_until_text: str,
    medical_decision: str,
    restriction_note: str,
) -> None:
    """Створює новий медичний запис і синхронізує контрольні сповіщення.
    Creates a new medical record and synchronizes control notifications.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_medical_decision = medical_decision.strip()
    normalized_restriction_note = restriction_note.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_medical_decision:
        raise ValueError("Потрібно вибрати медичне рішення.")

    valid_from = parse_ui_date_text(valid_from_text)
    valid_until = parse_ui_date_text(valid_until_text)
    if valid_until < valid_from:
        raise ValueError("Дата завершення не може бути раніше дати початку.")

    connection = create_database_connection(database_path)
    try:
        insert_medical_record(
            connection,
            MedicalRecord(
                record_id=None,
                employee_personnel_number=normalized_personnel_number,
                employee_full_name="",
                valid_from=valid_from.isoformat(),
                valid_until=valid_until.isoformat(),
                medical_decision=MedicalDecision(normalized_medical_decision),
                restriction_note=normalized_restriction_note,
                status=MedicalStatus.CURRENT,
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
