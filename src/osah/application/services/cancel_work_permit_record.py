from datetime import datetime
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.infrastructure.database.commands.cancel_work_permit_record_row import cancel_work_permit_record_row
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


# ###### СКАСУВАННЯ НАРЯДУ-ДОПУСКУ / CANCEL WORK PERMIT ######
def cancel_work_permit_record(database_path: Path, record_id: int, cancel_reason_text: str) -> None:
    """Скасовує наряд-допуск із фіксацією причини та audit-подією.
    Cancels a work permit with a reason and audit event.
    """

    normalized_reason = cancel_reason_text.strip()
    if not normalized_reason:
        raise ValueError("Потрібно вказати причину скасування наряду.")

    connection = create_database_connection(database_path)
    try:
        work_permit_record = next((item for item in list_work_permit_records(connection) if item.record_id == record_id), None)
        if work_permit_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")
        if work_permit_record.closed_at:
            raise ValueError("Закритий наряд не можна скасувати.")
        if work_permit_record.canceled_at:
            raise ValueError("Обраний наряд уже скасовано.")

        canceled_at = datetime.now().isoformat(sep=" ", timespec="minutes")
        cancel_work_permit_record_row(connection, record_id, canceled_at, normalized_reason)
        insert_audit_log(
            connection,
            event_type="work_permit.canceled",
            module_name="work_permits",
            event_level="warning",
            actor_name="system",
            entity_name=f"work_permit:{work_permit_record.permit_number}",
            result_status="success",
            description_text=(
                f"before=({serialize_work_permit_record_for_audit(work_permit_record)});"
                f"canceled_at={canceled_at};reason={normalized_reason}"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
