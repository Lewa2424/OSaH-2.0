from dataclasses import replace
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.application.services.sync_work_permit_target_training_records import sync_work_permit_target_training_records
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.domain.services.validate_work_permit_participant_change import validate_work_permit_participant_change
from osah.infrastructure.database.commands.delete_work_permit_participants import delete_work_permit_participants
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_work_permit_participant import insert_work_permit_participant
from osah.infrastructure.database.commands.update_work_permit_record_row import update_work_permit_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


def change_work_permit_participants(
    database_path: Path,
    record_id: int,
    participants: tuple[WorkPermitParticipant, ...],
) -> None:
    """Изменяет состав бригады наряда отдельной контролируемой операцией.
    Changes the permit brigade through a dedicated controlled operation.
    """

    connection = create_database_connection(database_path)
    try:
        previous_record = next(
            (item for item in list_work_permit_records(connection) if item.record_id == record_id),
            None,
        )
        if previous_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")
        if previous_record.closed_at or previous_record.canceled_at:
            raise ValueError("Закритий або скасований наряд не дозволяє змінювати склад бригади.")

        validate_work_permit_participant_change(previous_record.participants, participants)
        updated_record = replace(previous_record, participants=participants)
        if updated_record.participants == previous_record.participants:
            return

        update_work_permit_record_row(connection, updated_record)
        delete_work_permit_participants(connection, record_id)
        for participant in updated_record.participants:
            insert_work_permit_participant(connection, record_id, participant)
        sync_work_permit_target_training_records(connection, updated_record)
        insert_audit_log(
            connection,
            event_type="work_permit.participants_changed",
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
