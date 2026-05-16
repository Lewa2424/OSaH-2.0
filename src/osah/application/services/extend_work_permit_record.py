from dataclasses import replace
from datetime import datetime
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.domain.services.validate_work_permit_timeline import validate_work_permit_extension
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_work_permit_record_row import update_work_permit_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


def extend_work_permit_record(
    database_path: Path,
    record_id: int,
    extended_until_text: str,
    extension_reason_text: str,
) -> None:
    """Продовжує наряд-допуск один раз у межах ще 15 календарних днів.
    Extends a work permit once within another 15 calendar days.
    """

    normalized_reason = extension_reason_text.strip()
    if not normalized_reason:
        raise ValueError("Потрібно вказати причину продовження наряду-допуску.")

    extended_until = parse_ui_datetime_text(extended_until_text)
    connection = create_database_connection(database_path)
    try:
        previous_record = next((item for item in list_work_permit_records(connection) if item.record_id == record_id), None)
        if previous_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")

        validate_work_permit_extension(previous_record, extended_until)
        extended_at = datetime.now().isoformat(sep=" ", timespec="minutes")
        updated_record = replace(
            previous_record,
            ends_at=extended_until.isoformat(sep=" ", timespec="minutes"),
            extension_count=1,
            extended_at=extended_at,
            extension_reason_text=normalized_reason,
        )
        update_work_permit_record_row(connection, updated_record)
        insert_audit_log(
            connection,
            event_type="work_permit.extended",
            module_name="work_permits",
            event_level="info",
            actor_name="system",
            entity_name=f"work_permit:{updated_record.permit_number}",
            result_status="success",
            description_text=(
                f"before=({serialize_work_permit_record_for_audit(previous_record)});"
                f"after=({serialize_work_permit_record_for_audit(updated_record)})"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
