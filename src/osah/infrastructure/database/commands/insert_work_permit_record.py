from sqlite3 import Connection

from osah.domain.entities.work_permit_record import WorkPermitRecord


# ###### ДОБАВЛЕНИЕ НАРЯДА-ДОПУСКА / INSERT WORK PERMIT ######
def insert_work_permit_record(connection: Connection, work_permit_record: WorkPermitRecord) -> int:
    """Сохраняет новый наряд-допуск с полями целевого инструктажа.
    Persists a new work permit with targeted-training fields.
    """

    cursor = connection.execute(
        """
        INSERT INTO work_permits (
            permit_number,
            work_kind,
            work_location,
            starts_at,
            ends_at,
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            work_permit_record.permit_number,
            work_permit_record.work_kind,
            work_permit_record.work_location,
            work_permit_record.starts_at,
            work_permit_record.ends_at,
            work_permit_record.responsible_person,
            work_permit_record.issuer_person,
            work_permit_record.note_text,
            work_permit_record.closed_at,
            work_permit_record.canceled_at,
            work_permit_record.cancel_reason_text,
            work_permit_record.target_training_status.value,
            work_permit_record.target_training_date,
            work_permit_record.target_training_conducted_by,
            work_permit_record.target_training_note,
            work_permit_record.basis_text,
            work_permit_record.basis_note,
        ),
    )
    return int(cursor.lastrowid)
