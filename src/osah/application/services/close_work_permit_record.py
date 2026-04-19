from datetime import datetime
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.infrastructure.database.commands.close_work_permit_record_row import close_work_permit_record_row
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


# ###### ЗАКРИТТЯ НАРЯДУ-ДОПУСКУ / ЗАКРЫТИЕ НАРЯДА-ДОПУСКА ######
def close_work_permit_record(database_path: Path, record_id: int) -> None:
    """Закриває наряд-допуск вручну та синхронізує контрольні сповіщення.
    Закрывает наряд-допуск вручную и синхронизирует контрольные уведомления.
    """

    connection = create_database_connection(database_path)
    try:
        work_permit_record = next(
            (candidate_record for candidate_record in list_work_permit_records(connection) if candidate_record.record_id == record_id),
            None,
        )
        if work_permit_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")
        if work_permit_record.closed_at:
            raise ValueError("Обраний наряд-допуск уже закрито.")

        closed_at = datetime.now().isoformat(sep=" ", timespec="minutes")
        close_work_permit_record_row(connection, record_id, closed_at)
        insert_audit_log(
            connection,
            event_type="work_permit.closed",
            module_name="work_permits",
            event_level="info",
            actor_name="system",
            entity_name=f"work_permit:{work_permit_record.permit_number}",
            result_status="success",
            description_text=(
                f"before=({serialize_work_permit_record_for_audit(work_permit_record)});"
                f"closed_at={closed_at}"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
