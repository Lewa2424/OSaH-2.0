from sqlite3 import Connection

from osah.domain.entities.work_permit_participant import WorkPermitParticipant
from osah.domain.entities.work_permit_participant_role import WorkPermitParticipantRole
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.evaluate_work_permit_status import evaluate_work_permit_status


# ###### ЧИТАННЯ РЕЄСТРУ НАРЯДІВ-ДОПУСКІВ / ЧТЕНИЕ РЕЕСТРА НАРЯДОВ-ДОПУСКОВ ######
def list_work_permit_records(connection: Connection) -> tuple[WorkPermitRecord, ...]:
    """Повертає всі наряди-допуски з учасниками та розрахованими статусами.
    Возвращает все наряды-допуски с участниками и рассчитанными статусами.
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
            responsible_person,
            issuer_person,
            note_text,
            closed_at
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

    participants_by_permit_id: dict[int, list[WorkPermitParticipant]] = {}
    for row in participant_rows:
        participants_by_permit_id.setdefault(int(row["work_permit_id"]), []).append(
            WorkPermitParticipant(
                employee_personnel_number=row["employee_personnel_number"],
                employee_full_name=row["full_name"],
                participant_role=WorkPermitParticipantRole(row["participant_role"]),
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
            responsible_person=row["responsible_person"],
            issuer_person=row["issuer_person"],
            note_text=row["note_text"] or "",
            closed_at=row["closed_at"],
            participants=tuple(participants_by_permit_id.get(int(row["id"]), ())),
            status=WorkPermitStatus.ACTIVE,
        )
        records.append(
            WorkPermitRecord(
                record_id=work_permit_record.record_id,
                permit_number=work_permit_record.permit_number,
                work_kind=work_permit_record.work_kind,
                work_location=work_permit_record.work_location,
                starts_at=work_permit_record.starts_at,
                ends_at=work_permit_record.ends_at,
                responsible_person=work_permit_record.responsible_person,
                issuer_person=work_permit_record.issuer_person,
                note_text=work_permit_record.note_text,
                closed_at=work_permit_record.closed_at,
                participants=work_permit_record.participants,
                status=evaluate_work_permit_status(work_permit_record),
            )
        )

    return tuple(records)
