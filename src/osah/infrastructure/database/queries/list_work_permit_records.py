from sqlite3 import Connection

from osah.domain.entities.work_permit_daily_check import WorkPermitDailyCheck
from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.evaluate_work_permit_status import evaluate_work_permit_status
from osah.domain.services.normalize_work_permit_target_training_status import normalize_work_permit_target_training_status


# ###### ЧТЕНИЕ РЕЕСТРА НАРЯДОВ-ДОПУСКОВ / LIST WORK PERMIT RECORDS ######
def list_work_permit_records(connection: Connection) -> tuple[WorkPermitRecord, ...]:
    """Возвращает все наряды-допуски с полями целевого инструктажа и статусами.
    Returns all work permits with targeted-training fields and statuses.
    """

    permit_rows = connection.execute(
        """
        SELECT
            id,
            permit_number,
            work_kind,
            work_location,
            starts_at,
            ends_at,
            reissued_from_record_id,
            reissued_to_record_id,
            reissue_reason_text,
            base_ends_at,
            extension_count,
            extended_at,
            extension_reason_text,
            responsible_person,
            issuer_person,
            note_text,
            closed_at,
            canceled_at,
            cancel_reason_text,
            target_training_status,
            target_training_date,
            target_training_conducted_by,
            target_training_note,
            basis_text,
            basis_note
        FROM work_permits
        ORDER BY CASE WHEN closed_at IS NULL THEN 0 ELSE 1 END, ends_at ASC, id ASC;
        """
    ).fetchall()
    participant_rows = connection.execute(
        """
        SELECT
            work_permit_participants.work_permit_id,
            work_permit_participants.employee_personnel_number,
            employees.full_name,
            work_permit_participants.participant_role
        FROM work_permit_participants
        INNER JOIN employees
            ON employees.personnel_number = work_permit_participants.employee_personnel_number
        ORDER BY work_permit_participants.work_permit_id ASC, work_permit_participants.id ASC;
        """
    ).fetchall()
    daily_check_rows = connection.execute(
        """
        SELECT
            id,
            work_permit_id,
            checked_at,
            checked_by,
            note_text
        FROM work_permit_daily_checks
        ORDER BY work_permit_id ASC, checked_at ASC, id ASC;
        """
    ).fetchall()

    participants_by_permit_id: dict[int, list[WorkPermitParticipant]] = {}
    for row in participant_rows:
        participants_by_permit_id.setdefault(int(row["work_permit_id"]), []).append(
            WorkPermitParticipant(
                employee_personnel_number=row["employee_personnel_number"],
                employee_full_name=row["full_name"],
                participant_role=WorkPermitParticipantRole(row["participant_role"]),
            )
        )
    daily_checks_by_permit_id: dict[int, list[WorkPermitDailyCheck]] = {}
    for row in daily_check_rows:
        daily_checks_by_permit_id.setdefault(int(row["work_permit_id"]), []).append(
            WorkPermitDailyCheck(
                check_id=int(row["id"]),
                checked_at=row["checked_at"],
                checked_by=row["checked_by"],
                note_text=row["note_text"] or "",
            )
        )

    records: list[WorkPermitRecord] = []
    for row in permit_rows:
        work_permit_record = WorkPermitRecord(
            record_id=int(row["id"]),
            permit_number=row["permit_number"],
            work_kind=row["work_kind"],
            work_location=row["work_location"],
            starts_at=row["starts_at"],
            ends_at=row["ends_at"],
            reissued_from_record_id=row["reissued_from_record_id"],
            reissued_to_record_id=row["reissued_to_record_id"],
            reissue_reason_text=row["reissue_reason_text"] or "",
            base_ends_at=row["base_ends_at"] or row["ends_at"],
            extension_count=int(row["extension_count"] or 0),
            extended_at=row["extended_at"],
            extension_reason_text=row["extension_reason_text"] or "",
            responsible_person=row["responsible_person"],
            issuer_person=row["issuer_person"],
            note_text=row["note_text"] or "",
            closed_at=row["closed_at"],
            canceled_at=row["canceled_at"],
            cancel_reason_text=row["cancel_reason_text"] or "",
            participants=tuple(participants_by_permit_id.get(int(row["id"]), ())),
            daily_checks=tuple(daily_checks_by_permit_id.get(int(row["id"]), ())),
            status=WorkPermitStatus.ACTIVE,
            target_training_status=normalize_work_permit_target_training_status(
                WorkPermitTargetTrainingStatus(row["target_training_status"] or "legacy_not_tracked")
            ),
            target_training_date=row["target_training_date"] or "",
            target_training_conducted_by=row["target_training_conducted_by"] or "",
            target_training_note=row["target_training_note"] or "",
            basis_text=row["basis_text"] or "",
            basis_note=row["basis_note"] or "",
        )
        records.append(
            WorkPermitRecord(
                record_id=work_permit_record.record_id,
                permit_number=work_permit_record.permit_number,
                work_kind=work_permit_record.work_kind,
                work_location=work_permit_record.work_location,
                starts_at=work_permit_record.starts_at,
                ends_at=work_permit_record.ends_at,
                reissued_from_record_id=work_permit_record.reissued_from_record_id,
                reissued_to_record_id=work_permit_record.reissued_to_record_id,
                reissue_reason_text=work_permit_record.reissue_reason_text,
                base_ends_at=work_permit_record.base_ends_at,
                extension_count=work_permit_record.extension_count,
                extended_at=work_permit_record.extended_at,
                extension_reason_text=work_permit_record.extension_reason_text,
                responsible_person=work_permit_record.responsible_person,
                issuer_person=work_permit_record.issuer_person,
                note_text=work_permit_record.note_text,
                closed_at=work_permit_record.closed_at,
                participants=work_permit_record.participants,
                daily_checks=work_permit_record.daily_checks,
                status=evaluate_work_permit_status(work_permit_record),
                canceled_at=work_permit_record.canceled_at,
                cancel_reason_text=work_permit_record.cancel_reason_text,
                target_training_status=work_permit_record.target_training_status,
                target_training_date=work_permit_record.target_training_date,
                target_training_conducted_by=work_permit_record.target_training_conducted_by,
                target_training_note=work_permit_record.target_training_note,
                basis_text=work_permit_record.basis_text,
                basis_note=work_permit_record.basis_note,
            )
        )

    return tuple(records)
