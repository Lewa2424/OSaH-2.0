from sqlite3 import Connection

from osah.domain.entities.work_permit_record import WorkPermitRecord


# ###### ОНОВЛЕННЯ НАРЯДУ-ДОПУСКУ / UPDATE WORK PERMIT ######
def update_work_permit_record_row(connection: Connection, work_permit_record: WorkPermitRecord) -> None:
    """Оновлює основні поля наряду-допуску в локальній базі.
    Updates main work permit fields in the local database.
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
            note_text = ?
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
            work_permit_record.record_id,
        ),
    )
