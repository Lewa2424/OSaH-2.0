from sqlite3 import Connection

from osah.domain.entities.medical_record import MedicalRecord


# ###### ДОДАВАННЯ МЕДИЧНОГО ЗАПИСУ / ДОБАВЛЕНИЕ МЕДИЦИНСКОЙ ЗАПИСИ ######
def insert_medical_record(connection: Connection, medical_record: MedicalRecord) -> None:
    """Зберігає новий медичний запис у локальній базі.
    Сохраняет новую медицинскую запись в локальной базе.
    """

    connection.execute(
        """
        INSERT INTO medical_records (
            employee_personnel_number,
            valid_from,
            valid_until,
            medical_decision,
            restriction_note
        )
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            medical_record.employee_personnel_number,
            medical_record.valid_from,
            medical_record.valid_until,
            medical_record.medical_decision.value,
            medical_record.restriction_note,
        ),
    )
