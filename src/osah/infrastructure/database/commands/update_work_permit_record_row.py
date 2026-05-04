from sqlite3 import Connection

from osah.domain.entities.work_permit_record import WorkPermitRecord


# ###### ОБНОВЛЕНИЕ НАРЯДА-ДОПУСКА / UPDATE WORK PERMIT ######
def update_work_permit_record_row(connection: Connection, work_permit_record: WorkPermitRecord) -> None:
    """Обновляет основные поля наряда и поля целевого инструктажа.
    Updates main work-permit fields and targeted-training fields.
    """

    connection.execute(
        """
        UPDATE work_permits
        SET
            permit_number = ?,
            work_kind = ?,
            work_location = ?,
            starts_at = ?,
            ends_at = ?,
            responsible_person = ?,
            issuer_person = ?,
            note_text = ?,
            target_training_status = ?,
            target_training_date = ?,
            target_training_conducted_by = ?,
            target_training_note = ?,
            basis_text = ?,
            basis_note = ?
        WHERE id = ?;
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
            work_permit_record.target_training_status.value,
            work_permit_record.target_training_date,
            work_permit_record.target_training_conducted_by,
            work_permit_record.target_training_note,
            work_permit_record.basis_text,
            work_permit_record.basis_note,
            work_permit_record.record_id,
        ),
    )
