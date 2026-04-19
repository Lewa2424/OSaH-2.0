from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.services.serialize_training_record_for_audit import serialize_training_record_for_audit
from osah.infrastructure.database.commands.delete_training_record_row import delete_training_record_row
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_training_record_by_id import get_training_record_by_id


# ###### ВИДАЛЕННЯ ЗАПИСУ ІНСТРУКТАЖУ / УДАЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА ######
def delete_training_record(database_path: Path, record_id: int) -> None:
    """Видаляє запис інструктажу, синхронізує сповіщення і пише audit.
    Удаляет запись инструктажа, синхронизирует уведомления и пишет audit.
    """

    connection = create_database_connection(database_path)
    try:
        previous_record = get_training_record_by_id(connection, record_id)
        if previous_record is None:
            raise ValueError("Запис інструктажу не знайдено.")

        delete_training_record_row(connection, record_id)
        insert_audit_log(
            connection,
            event_type="training.deleted",
            module_name="trainings",
            event_level="warning",
            actor_name="system",
            entity_name=f"training:{record_id}",
            result_status="success",
            description_text=f"deleted=({serialize_training_record_for_audit(previous_record)})",
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
