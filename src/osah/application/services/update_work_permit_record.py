from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.infrastructure.database.commands.delete_work_permit_participants import delete_work_permit_participants
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_work_permit_participant import insert_work_permit_participant
from osah.infrastructure.database.commands.update_work_permit_record_row import update_work_permit_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


# ###### ОНОВЛЕННЯ НАРЯДУ-ДОПУСКУ / UPDATE WORK PERMIT RECORD ######
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
) -> None:
    """Оновлює наряд-допуск та контрольований список учасників через application service.
    Updates a work permit and the controlled participant list through an application service.
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
    )
    connection = create_database_connection(database_path)
    try:
        previous_record = next((item for item in list_work_permit_records(connection) if item.record_id == record_id), None)
        if previous_record is None:
            raise ValueError("Обраний наряд-допуск не знайдено.")
        if previous_record.closed_at or previous_record.canceled_at:
            raise ValueError("Закритий або скасований наряд не редагується.")

        updated_record = WorkPermitRecord(
            record_id=record_id,
            status=WorkPermitStatus.ACTIVE,
            closed_at=None,
            canceled_at=None,
            cancel_reason_text="",
            **normalized,
        )
        update_work_permit_record_row(connection, updated_record)
        delete_work_permit_participants(connection, record_id)
        for participant in updated_record.participants:
            insert_work_permit_participant(connection, record_id, participant)
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


# ###### ВАЛІДАЦІЯ НАРЯДУ / VALIDATE WORK PERMIT INPUT ######
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
) -> dict[str, object]:
    """Перевіряє поля наряду та повертає нормалізовані значення.
    Validates work permit fields and returns normalized values.
    """

    starts_at = parse_ui_datetime_text(starts_at_text)
    ends_at = parse_ui_datetime_text(ends_at_text)
    if ends_at <= starts_at:
        raise ValueError("Час завершення має бути пізніше часу початку.")

    normalized_permit_number = permit_number.strip()
    normalized_work_kind = work_kind.strip()
    normalized_work_location = work_location.strip()
    normalized_responsible_person = responsible_person.strip()
    normalized_issuer_person = issuer_person.strip()
    normalized_employee_personnel_number = employee_personnel_number.strip()
    normalized_participant_role = participant_role.strip()
    if not normalized_permit_number or not normalized_work_kind or not normalized_work_location:
        raise ValueError("Номер наряду, вид робіт і місце робіт обов'язкові.")
    if not normalized_responsible_person or not normalized_issuer_person:
        raise ValueError("Потрібно вказати відповідального та допускаючого.")
    if not normalized_employee_personnel_number:
        raise ValueError("Потрібно вибрати учасника наряду.")

    return {
        "permit_number": normalized_permit_number,
        "work_kind": normalized_work_kind,
        "work_location": normalized_work_location,
        "starts_at": starts_at.isoformat(sep=" ", timespec="minutes"),
        "ends_at": ends_at.isoformat(sep=" ", timespec="minutes"),
        "responsible_person": normalized_responsible_person,
        "issuer_person": normalized_issuer_person,
        "note_text": note_text.strip(),
        "participants": (
            WorkPermitParticipant(
                employee_personnel_number=normalized_employee_personnel_number,
                employee_full_name="",
                participant_role=WorkPermitParticipantRole(normalized_participant_role),
            ),
        ),
    }
