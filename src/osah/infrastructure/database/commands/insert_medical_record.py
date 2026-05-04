from sqlite3 import Connection

from osah.domain.entities.medical_record import MedicalRecord


# ###### ДОБАВЛЕНИЕ МЕДИЦИНСКОЙ ЗАПИСИ / INSERT MEDICAL RECORD ######
def insert_medical_record(connection: Connection, medical_record: MedicalRecord) -> None:
    """Сохраняет новую медицинскую запись с основанием и примечанием.
    Persists a new medical record with basis and note fields.
    """

    connection.execute(
        """
        INSERT INTO medical_records (
            employee_personnel_number,
            valid_from,
            valid_until,
            medical_decision,
            restriction_note,
            medical_exam_basis,
            basis_text,
            basis_note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
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
        ),
    )
