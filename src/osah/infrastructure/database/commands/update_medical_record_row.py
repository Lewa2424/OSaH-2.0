from sqlite3 import Connection

from osah.domain.entities.medical_record import MedicalRecord


# ###### ОБНОВЛЕНИЕ МЕДИЦИНСКОЙ ЗАПИСИ / UPDATE MEDICAL RECORD ######
def update_medical_record_row(connection: Connection, medical_record: MedicalRecord) -> None:
    """Обновляет существующую медицинскую запись с новыми полями основания.
    Updates an existing medical record including the new basis fields.
    """

    connection.execute(
        """
        UPDATE medical_records
        SET
            employee_personnel_number = ?,
            valid_from = ?,
            valid_until = ?,
            medical_decision = ?,
            restriction_note = ?,
            medical_exam_basis = ?,
            basis_text = ?,
            basis_note = ?
        WHERE id = ?;
        """,
        (
            medical_record.employee_personnel_number,
            medical_record.valid_from,
            medical_record.valid_until,
            medical_record.medical_decision.value,
            medical_record.restriction_note,
            medical_record.medical_exam_basis.value,
            medical_record.basis_text,
            medical_record.basis_note,
            medical_record.record_id,
        ),
    )
