from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.work_permit_daily_check import WorkPermitDailyCheck
from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.domain.services.validate_work_permit_daily_check import validate_work_permit_daily_check
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_work_permit_daily_check import insert_work_permit_daily_check
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


def record_work_permit_daily_check(
    database_path: Path,
    record_id: int,
    checked_at_text: str,
    checked_by: str,
    note_text: str = "",
    *,
    access_role: AccessRole,
) -> None:
    """Фіксує щоденну перевірку місця виконання робіт за нарядом.
    Records a daily check for the work area under a permit.
    """

    ensure_write_access(access_role, "record_work_permit_daily_check")
    checked_at = parse_ui_datetime_text(checked_at_text)
    normalized_checked_by = checked_by.strip()
    normalized_note_text = note_text.strip()
    connection = create_database_connection(database_path)
    try:
        work_permit_record = next(
            (candidate_record for candidate_record in list_work_permit_records(connection) if candidate_record.record_id == record_id),
            None,
        )
        if work_permit_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")

        validate_work_permit_daily_check(work_permit_record, checked_at, normalized_checked_by)
        daily_check = WorkPermitDailyCheck(
            check_id=None,
            checked_at=checked_at.isoformat(sep=" ", timespec="minutes"),
            checked_by=normalized_checked_by,
            note_text=normalized_note_text,
        )
        insert_work_permit_daily_check(connection, record_id, daily_check)
        insert_audit_log(
            connection,
            event_type="work_permit.daily_check_recorded",
            module_name="work_permits",
            event_level="info",
            actor_name="system",
            entity_name=f"work_permit:{work_permit_record.permit_number}",
            result_status="success",
            description_text=(
                f"before=({serialize_work_permit_record_for_audit(work_permit_record)});"
                f"checked_at={daily_check.checked_at};"
                f"checked_by={daily_check.checked_by};"
                f"note_text={daily_check.note_text}"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
