from sqlite3 import Connection

from osah.domain.entities.ppe_record import PpeRecord


# ###### ОНОВЛЕННЯ ЗАПИСУ ЗІЗ / UPDATE PPE RECORD ######
def update_ppe_record_row(connection: Connection, ppe_record: PpeRecord) -> None:
    """Оновлює існуючий запис ЗІЗ у локальній базі.
    Updates an existing PPE record in the local database.
    """

    connection.execute(
        """
        UPDATE ppe_records
        SET
            employee_personnel_number = ?,
            ppe_name = ?,
            is_required = ?,
            is_issued = ?,
            issue_date = ?,
            replacement_date = ?,
            quantity = ?,
            note_text = ?
        WHERE id = ?;
        """,
        (
            ppe_record.employee_personnel_number,
            ppe_record.ppe_name,
            1 if ppe_record.is_required else 0,
            1 if ppe_record.is_issued else 0,
            ppe_record.issue_date,
            ppe_record.replacement_date,
            ppe_record.quantity,
            ppe_record.note_text,
            ppe_record.record_id,
        ),
    )
