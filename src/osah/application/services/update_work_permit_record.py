from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.application.services.sync_work_permit_target_training_records import sync_work_permit_target_training_records
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.has_work_permit_participant_composition_changed import (
    has_work_permit_participant_composition_changed,
)
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.domain.services.validate_work_permit_timeline import validate_work_permit_base_timeline
from osah.infrastructure.database.commands.delete_work_permit_participants import delete_work_permit_participants
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_work_permit_participant import insert_work_permit_participant
from osah.infrastructure.database.commands.update_work_permit_record_row import update_work_permit_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


def update_work_permit_record(
    database_path: Path,
    record_id: int,
    permit_number: str,
    work_kind: str,
    work_location: str,
    starts_at_text: str,
    ends_at_text: str,
    responsible_person: str,
    issuer_person: str,
    employee_personnel_number: str,
    participant_role: str,
    note_text: str,
    target_training_status: str = "legacy_not_tracked",
    target_training_date_text: str = "",
    target_training_conducted_by: str = "",
    target_training_note: str = "",
    basis_text: str = "",
    basis_note: str = "",
    participants: tuple[WorkPermitParticipant, ...] | None = None,
) -> None:
    """Оновлює наряд-допуск.
    Updates a work permit.
    """

    normalized = _validate_work_permit_input(
        permit_number,
        work_kind,
        work_location,
        starts_at_text,
        ends_at_text,
        responsible_person,
        issuer_person,
        employee_personnel_number,
        participant_role,
        note_text,
        target_training_status,
        target_training_date_text,
        target_training_conducted_by,
        target_training_note,
        basis_text,
        basis_note,
        participants=participants,
    )
    connection = create_database_connection(database_path)
    try:
        previous_record = next((item for item in list_work_permit_records(connection) if item.record_id == record_id), None)
        if previous_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")
        if previous_record.closed_at or previous_record.canceled_at:
            raise ValueError("Закритий або скасований наряд не редагується.")
        if previous_record.extension_count > 0 and (
            str(normalized["starts_at"]) != previous_record.starts_at or str(normalized["ends_at"]) != previous_record.ends_at
        ):
            raise ValueError("Після продовження строку дії дати наряду змінюються лише через окрему дію продовження.")
        if (
            str(normalized["work_kind"]) != previous_record.work_kind
            or str(normalized["work_location"]) != previous_record.work_location
        ):
            raise ValueError("Зміну виду робіт або місця виконання оформлюйте через окремий перевипуск наряду.")
        if participants is not None and has_work_permit_participant_composition_changed(
            previous_record.participants,
            normalized["participants"],
        ):
            raise ValueError("Зміну складу бригади виконуйте окремою дією, а не через загальне редагування наряду.")

        updated_record = WorkPermitRecord(
            record_id=record_id,
            status=WorkPermitStatus.ACTIVE,
            closed_at=None,
            canceled_at=None,
            cancel_reason_text="",
            daily_checks=previous_record.daily_checks,
            reissued_from_record_id=previous_record.reissued_from_record_id,
            reissued_to_record_id=previous_record.reissued_to_record_id,
            reissue_reason_text=previous_record.reissue_reason_text,
            base_ends_at=previous_record.base_ends_at if previous_record.extension_count > 0 else str(normalized["ends_at"]),
            extension_count=previous_record.extension_count,
            extended_at=previous_record.extended_at,
            extension_reason_text=previous_record.extension_reason_text,
            **normalized,
        )
        update_work_permit_record_row(connection, updated_record)
        delete_work_permit_participants(connection, record_id)
        for participant in updated_record.participants:
            insert_work_permit_participant(connection, record_id, participant)
        sync_work_permit_target_training_records(connection, updated_record)
        insert_audit_log(
            connection,
            event_type="work_permit.updated",
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


def _validate_work_permit_input(
    permit_number: str,
    work_kind: str,
    work_location: str,
    starts_at_text: str,
    ends_at_text: str,
    responsible_person: str,
    issuer_person: str,
    employee_personnel_number: str,
    participant_role: str,
    note_text: str,
    target_training_status: str,
    target_training_date_text: str,
    target_training_conducted_by: str,
    target_training_note: str,
    basis_text: str,
    basis_note: str,
    participants: tuple[WorkPermitParticipant, ...] | None = None,
) -> dict[str, object]:
    starts_at = parse_ui_datetime_text(starts_at_text)
    ends_at = parse_ui_datetime_text(ends_at_text)
    validate_work_permit_base_timeline(starts_at, ends_at)

    normalized_permit_number = permit_number.strip()
    normalized_work_kind = work_kind.strip()
    normalized_work_location = work_location.strip()
    normalized_responsible_person = responsible_person.strip()
    normalized_issuer_person = issuer_person.strip()
    normalized_employee_personnel_number = employee_personnel_number.strip()
    normalized_participant_role = participant_role.strip()
    if not normalized_permit_number or not normalized_work_kind or not normalized_work_location:
        raise ValueError("Номер наряду, вид робіт і місце робіт обов'язкові.")
    if not normalized_responsible_person:
        raise ValueError("Потрібно вказати керівника робіт.")

    target_training_date = ""
    if target_training_date_text.strip():
        target_training_date = parse_ui_date_text(target_training_date_text.strip()).isoformat()
    normalized_target_training_status = WorkPermitTargetTrainingStatus(target_training_status.strip() or "legacy_not_tracked")
    normalized_target_training_conducted_by = target_training_conducted_by.strip()
    if normalized_target_training_status in {
        WorkPermitTargetTrainingStatus.DONE_PASSED,
        WorkPermitTargetTrainingStatus.DONE_FAILED,
        WorkPermitTargetTrainingStatus.DONE,
    } and (not target_training_date or not normalized_target_training_conducted_by):
        raise ValueError("Для проведеного цільового інструктажу потрібно вказати дату та особу, яка його провела.")

    effective_participants: tuple[WorkPermitParticipant, ...]
    if participants is not None:
        effective_participants = participants
    elif normalized_employee_personnel_number:
        effective_participants = (
            WorkPermitParticipant(
                employee_personnel_number=normalized_employee_personnel_number,
                employee_full_name="",
                participant_role=WorkPermitParticipantRole(
                    normalized_participant_role or WorkPermitParticipantRole.EXECUTOR.value
                ),
            ),
        )
    else:
        effective_participants = ()

    return {
        "permit_number": normalized_permit_number,
        "work_kind": normalized_work_kind,
        "work_location": normalized_work_location,
        "starts_at": starts_at.isoformat(sep=" ", timespec="minutes"),
        "ends_at": ends_at.isoformat(sep=" ", timespec="minutes"),
        "responsible_person": normalized_responsible_person,
        "issuer_person": normalized_issuer_person,
        "note_text": note_text.strip(),
        "participants": effective_participants,
        "target_training_status": normalized_target_training_status,
        "target_training_date": target_training_date,
        "target_training_conducted_by": normalized_target_training_conducted_by,
        "target_training_note": target_training_note.strip(),
        "basis_text": basis_text.strip(),
        "basis_note": basis_note.strip(),
    }
