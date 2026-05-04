from dataclasses import replace
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.application.services.sync_work_permit_target_training_records import sync_work_permit_target_training_records
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text
from osah.domain.services.serialize_work_permit_record_for_audit import serialize_work_permit_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_work_permit_participant import insert_work_permit_participant
from osah.infrastructure.database.commands.insert_work_permit_record import insert_work_permit_record
from osah.infrastructure.database.create_database_connection import create_database_connection


def create_work_permit_record(
    database_path: Path,
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
    """Створює новий наряд-допуск і синхронізує пов'язані записи.
    Creates a new work permit and synchronizes linked records.
    """

    normalized_permit_number = permit_number.strip()
    normalized_work_kind = work_kind.strip()
    normalized_work_location = work_location.strip()
    normalized_responsible_person = responsible_person.strip()
    normalized_issuer_person = issuer_person.strip()
    normalized_employee_personnel_number = employee_personnel_number.strip()
    normalized_note_text = note_text.strip()
    normalized_participant_role = participant_role.strip()
    if not normalized_permit_number:
        raise ValueError("Потрібно вказати номер наряду-допуску.")
    if not normalized_work_kind:
        raise ValueError("Потрібно вказати вид робіт.")
    if not normalized_work_location:
        raise ValueError("Потрібно вказати місце виконання робіт.")
    if not normalized_responsible_person:
        raise ValueError("Потрібно вказати керівника робіт.")
    if not normalized_issuer_person:
        raise ValueError("Потрібно вказати допускаючого.")
    if not normalized_employee_personnel_number and not participants:
        raise ValueError("Потрібно вибрати учасника наряду.")
    if not normalized_participant_role and not participants:
        raise ValueError("Потрібно вибрати роль учасника.")

    starts_at = parse_ui_datetime_text(starts_at_text)
    ends_at = parse_ui_datetime_text(ends_at_text)
    if ends_at <= starts_at:
        raise ValueError("Час завершення має бути пізніше часу початку.")

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

    effective_participants = participants or (
        WorkPermitParticipant(
            employee_personnel_number=normalized_employee_personnel_number,
            employee_full_name="",
            participant_role=WorkPermitParticipantRole(normalized_participant_role),
        ),
    )

    work_permit_record = WorkPermitRecord(
        record_id=None,
        permit_number=normalized_permit_number,
        work_kind=normalized_work_kind,
        work_location=normalized_work_location,
        starts_at=starts_at.isoformat(sep=" ", timespec="minutes"),
        ends_at=ends_at.isoformat(sep=" ", timespec="minutes"),
        responsible_person=normalized_responsible_person,
        issuer_person=normalized_issuer_person,
        note_text=normalized_note_text,
        closed_at=None,
        participants=effective_participants,
        status=WorkPermitStatus.ACTIVE,
        target_training_status=normalized_target_training_status,
        target_training_date=target_training_date,
        target_training_conducted_by=normalized_target_training_conducted_by,
        target_training_note=target_training_note.strip(),
        basis_text=basis_text.strip(),
        basis_note=basis_note.strip(),
    )

    connection = create_database_connection(database_path)
    try:
        work_permit_id = insert_work_permit_record(connection, work_permit_record)
        for work_permit_participant in work_permit_record.participants:
            insert_work_permit_participant(connection, work_permit_id, work_permit_participant)
        saved_work_permit_record = replace(work_permit_record, record_id=work_permit_id)
        sync_work_permit_target_training_records(connection, saved_work_permit_record)
        insert_audit_log(
            connection,
            event_type="work_permit.created",
            module_name="work_permits",
            event_level="info",
            actor_name="system",
            entity_name=f"work_permit:{normalized_permit_number}",
            result_status="success",
            description_text=f"created=({serialize_work_permit_record_for_audit(saved_work_permit_record)})",
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
