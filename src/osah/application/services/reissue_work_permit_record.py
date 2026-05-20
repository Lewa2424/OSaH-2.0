from dataclasses import replace
from datetime import datetime
from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.application.services.sync_work_permit_target_training_records import sync_work_permit_target_training_records
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_work_permit_participant import insert_work_permit_participant
from osah.infrastructure.database.commands.insert_work_permit_record import insert_work_permit_record
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


def reissue_work_permit_record(
    database_path: Path,
    source_record_id: int,
    reissued_record: WorkPermitRecord,
    reissue_reason_text: str,
    *,
    access_role: AccessRole,
) -> int:
    """Перевипускає наряд-допуск як новий запис.
    Reissues a work permit as a new record.
    """

    ensure_write_access(access_role, "reissue_work_permit_record")
    normalized_reason = reissue_reason_text.strip()
    if not normalized_reason:
        raise ValueError("Потрібно вказати причину перевипуску наряду.")

    connection = create_database_connection(database_path)
    try:
        source_record = next(
            (item for item in list_work_permit_records(connection) if item.record_id == source_record_id),
            None,
        )
        if source_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")
        if source_record.closed_at:
            raise ValueError("Закритий наряд не можна перевипустити.")
        if source_record.canceled_at:
            raise ValueError("Скасований наряд не можна перевипустити повторно.")
        if (
            source_record.work_kind == reissued_record.work_kind
            and source_record.work_location == reissued_record.work_location
            and source_record.starts_at == reissued_record.starts_at
            and source_record.ends_at == reissued_record.ends_at
            and _participant_keys(source_record) == _participant_keys(reissued_record)
        ):
            raise ValueError("Для перевипуску потрібно змінити вид робіт, місце, строк або склад бригади.")

        prepared_new_record = replace(
            reissued_record,
            record_id=None,
            status=WorkPermitStatus.ACTIVE,
            closed_at=None,
            canceled_at=None,
            cancel_reason_text="",
            daily_checks=(),
            reissued_from_record_id=source_record_id,
            reissued_to_record_id=None,
            reissue_reason_text=normalized_reason,
        )
        new_record_id = insert_work_permit_record(connection, prepared_new_record)
        for participant in prepared_new_record.participants:
            insert_work_permit_participant(connection, new_record_id, participant)
        saved_new_record = replace(prepared_new_record, record_id=new_record_id)
        sync_work_permit_target_training_records(connection, saved_new_record)

        canceled_at = datetime.now().isoformat(sep=" ", timespec="minutes")
        connection.execute(
            """
            UPDATE work_permits
            SET canceled_at = ?, cancel_reason_text = ?, reissued_to_record_id = ?, reissue_reason_text = ?
            WHERE id = ?;
            """,
            (
                canceled_at,
                f"Перевипуск: {normalized_reason}",
                new_record_id,
                normalized_reason,
                source_record_id,
            ),
        )
        updated_source_record = replace(
            source_record,
            canceled_at=canceled_at,
            cancel_reason_text=f"Перевипуск: {normalized_reason}",
            reissued_to_record_id=new_record_id,
            reissue_reason_text=normalized_reason,
            status=WorkPermitStatus.REISSUED,
        )
        insert_audit_log(
            connection,
            event_type="work_permit.reissued",
            module_name="work_permits",
            event_level="warning",
            actor_name="system",
            entity_name=f"work_permit:{source_record.permit_number}",
            result_status="success",
            description_text=(
                f"before=({serialize_work_permit_record_for_audit(source_record)});"
                f"after=({serialize_work_permit_record_for_audit(updated_source_record)});"
                f"new_record=({serialize_work_permit_record_for_audit(saved_new_record)})"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
        return int(new_record_id)
    finally:
        connection.close()


def _participant_keys(work_permit_record: WorkPermitRecord) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted(
            (
                participant.employee_personnel_number.strip(),
                participant.participant_role.value,
            )
            for participant in work_permit_record.participants
        )
    )
