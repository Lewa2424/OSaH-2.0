from sqlite3 import Connection

from osah.domain.entities.ppe_record import PpeRecord


# ###### ДОДАВАННЯ ЗАПИСУ ЗІЗ / ДОБАВЛЕНИЕ ЗАПИСИ СИЗ ######
def insert_ppe_record(connection: Connection, ppe_record: PpeRecord) -> None:
    """Зберігає новий запис ЗІЗ у локальній базі.
    Сохраняет новую запись СИЗ в локальной базе.
    """

    connection.execute(
        """
        INSERT INTO ppe_records (
            employee_personnel_number,
            ppe_name,
            is_required,
            is_issued,
            issue_date,
            replacement_date,
            quantity,
            note_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
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
        ),
    )
    connection.commit()
