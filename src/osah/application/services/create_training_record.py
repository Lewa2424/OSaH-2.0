from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.serialize_training_record_for_audit import serialize_training_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_training_record import insert_training_record
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СТВОРЕННЯ ЗАПИСУ ІНСТРУКТАЖУ / CREATE TRAINING RECORD ######
def create_training_record(
    database_path: Path,
    employee_personnel_number: str,
    training_type: str,
    event_date_text: str,
    next_control_date_text: str,
    conducted_by: str,
    note_text: str,
) -> None:
    """Створює новий запис інструктажу та синхронізує контрольні сповіщення.
    Creates a new training record and synchronizes control notifications.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_conducted_by = conducted_by.strip()
    normalized_note = note_text.strip()
    normalized_training_type = training_type.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_training_type:
        raise ValueError("Потрібно вибрати тип інструктажу.")
    if not normalized_conducted_by:
        raise ValueError("Потрібно вказати, хто проводив інструктаж.")

    event_date = parse_ui_date_text(event_date_text)
    next_control_date = parse_ui_date_text(next_control_date_text)
    if next_control_date < event_date:
        raise ValueError("Дата наступного контролю не може бути раніше дати проведення.")

    connection = create_database_connection(database_path)
    try:
        training_record = TrainingRecord(
            record_id=None,
            employee_personnel_number=normalized_personnel_number,
            employee_full_name="",
            training_type=TrainingType(normalized_training_type),
            event_date=event_date.isoformat(),
            next_control_date=next_control_date.isoformat(),
            conducted_by=normalized_conducted_by,
            note_text=normalized_note,
            status=TrainingStatus.CURRENT,
        )
        insert_training_record(connection, training_record)
        insert_audit_log(
            connection,
            event_type="training.created",
            module_name="trainings",
            event_level="info",
            actor_name="system",
            entity_name=f"training:{normalized_personnel_number}",
            result_status="success",
            description_text=f"created=({serialize_training_record_for_audit(training_record)})",
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
