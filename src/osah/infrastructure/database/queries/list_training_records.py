from sqlite3 import Connection

from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.evaluate_training_status import evaluate_training_status


# ###### ЧИТАННЯ РЕЄСТРУ ІНСТРУКТАЖІВ / ЧТЕНИЕ РЕЕСТРА ИНСТРУКТАЖЕЙ ######
def list_training_records(connection: Connection) -> tuple[TrainingRecord, ...]:
    """Повертає всі записи інструктажів із розрахованими статусами.
    Возвращает все записи инструктажей с рассчитанными статусами.
    """

    rows = connection.execute(
        """
        SELECT
            trainings.id,
            trainings.employee_personnel_number,
            employees.full_name,
            trainings.training_type,
            trainings.event_date,
            trainings.next_control_date,
            trainings.conducted_by,
            trainings.note_text
        FROM trainings
        INNER JOIN employees
            ON employees.personnel_number = trainings.employee_personnel_number
        ORDER BY trainings.next_control_date ASC, trainings.id ASC;
        """
    ).fetchall()

    records: list[TrainingRecord] = []
    for row in rows:
        training_record = TrainingRecord(
            record_id=int(row["id"]),
            employee_personnel_number=row["employee_personnel_number"],
            employee_full_name=row["full_name"],
            training_type=TrainingType(row["training_type"]),
            event_date=row["event_date"],
            next_control_date=row["next_control_date"],
            conducted_by=row["conducted_by"],
            note_text=row["note_text"] or "",
            status=TrainingStatus.CURRENT,
        )
        records.append(
            TrainingRecord(
                record_id=training_record.record_id,
                employee_personnel_number=training_record.employee_personnel_number,
                employee_full_name=training_record.employee_full_name,
                training_type=training_record.training_type,
                event_date=training_record.event_date,
                next_control_date=training_record.next_control_date,
                conducted_by=training_record.conducted_by,
                note_text=training_record.note_text,
                status=evaluate_training_status(training_record),
            )
        )

    return tuple(records)
