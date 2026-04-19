from sqlite3 import Connection

from osah.domain.entities.training_record import TrainingRecord


# ###### ОНОВЛЕННЯ ЗАПИСУ ІНСТРУКТАЖУ / ОБНОВЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА ######
def update_training_record_row(connection: Connection, training_record: TrainingRecord) -> None:
    """Оновлює існуючий запис інструктажу в локальній базі.
    Обновляет существующую запись инструктажа в локальной базе.
    """

    connection.execute(
        """
        UPDATE trainings
        SET
            employee_personnel_number = ?,
            training_type = ?,
            event_date = ?,
            next_control_date = ?,
            conducted_by = ?,
            note_text = ?
        WHERE id = ?;
        """,
        (
            training_record.employee_personnel_number,
            training_record.training_type.value,
            training_record.event_date,
            training_record.next_control_date,
            training_record.conducted_by,
            training_record.note_text,
            training_record.record_id,
        ),
    )
