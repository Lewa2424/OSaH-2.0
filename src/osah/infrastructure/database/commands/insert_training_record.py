from sqlite3 import Connection

from osah.domain.entities.training_record import TrainingRecord


# ###### ДОДАВАННЯ ЗАПИСУ ІНСТРУКТАЖУ / ДОБАВЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА ######
def insert_training_record(connection: Connection, training_record: TrainingRecord) -> None:
    """Зберігає новий запис інструктажу в локальній базі.
    Сохраняет новую запись инструктажа в локальной базе.
    """

    connection.execute(
        """
        INSERT INTO trainings (
            employee_personnel_number,
            training_type,
            event_date,
            next_control_date,
            conducted_by,
            note_text
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            training_record.employee_personnel_number,
            training_record.training_type.value,
            training_record.event_date,
            training_record.next_control_date,
            training_record.conducted_by,
            training_record.note_text,
        ),
    )
