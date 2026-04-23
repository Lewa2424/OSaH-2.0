from sqlite3 import Connection

from osah.domain.entities.medical_record import MedicalRecord


# ###### ОНОВЛЕННЯ МЕДИЧНОГО ЗАПИСУ / UPDATE MEDICAL RECORD ######
def update_medical_record_row(connection: Connection, medical_record: MedicalRecord) -> None:
    """Оновлює існуючий медичний запис у локальній базі.
    Updates an existing medical record in the local database.
    """

    connection.execute(
        """
        UPDATE medical_records
        SET
            employee_personnel_number = ?,
            valid_from = ?,
            valid_until = ?,
            medical_decision = ?,
            restriction_note = ?
        WHERE id = ?;
        """,
        (
            medical_record.employee_personnel_number,
            medical_record.valid_from,
            medical_record.valid_until,
            medical_record.medical_decision.value,
            medical_record.restriction_note,
            medical_record.record_id,
        ),
    )
