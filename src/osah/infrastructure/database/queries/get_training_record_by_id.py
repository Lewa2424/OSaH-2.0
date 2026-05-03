from sqlite3 import Connection

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.evaluate_training_status import evaluate_training_status


# ###### ЧТЕНИЕ ЗАПИСИ ИНСТРУКТАЖА ПО ID / GET TRAINING RECORD BY ID ######
def get_training_record_by_id(connection: Connection, record_id: int) -> TrainingRecord | None:
    """Возвращает одну запись инструктажа по идентификатору.
    Returns one training record by identifier.
    """

    row = connection.execute(
        """
        SELECT
            trainings.id,
            trainings.employee_personnel_number,
            employees.full_name,
            trainings.training_type,
            trainings.event_date,
            trainings.next_control_date,
            trainings.conducted_by,
            trainings.note_text,
            trainings.person_category,
            trainings.requires_primary_on_workplace,
            trainings.work_risk_category,
            trainings.next_control_basis
        FROM trainings
        INNER JOIN employees
            ON employees.personnel_number = trainings.employee_personnel_number
        WHERE trainings.id = ?;
        """,
        (record_id,),
    ).fetchone()
    if row is None:
        return None

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
        person_category=TrainingPersonCategory(row["person_category"] or "own_employee"),
        requires_primary_on_workplace=bool(int(row["requires_primary_on_workplace"] or 0)),
        work_risk_category=TrainingWorkRiskCategory(row["work_risk_category"] or "not_applicable"),
        next_control_basis=TrainingNextControlBasis(row["next_control_basis"] or "manual"),
    )
    return TrainingRecord(
        record_id=training_record.record_id,
        employee_personnel_number=training_record.employee_personnel_number,
        employee_full_name=training_record.employee_full_name,
        training_type=training_record.training_type,
        event_date=training_record.event_date,
        next_control_date=training_record.next_control_date,
        conducted_by=training_record.conducted_by,
        note_text=training_record.note_text,
        status=evaluate_training_status(training_record, (training_record,)),
        person_category=training_record.person_category,
        requires_primary_on_workplace=training_record.requires_primary_on_workplace,
        work_risk_category=training_record.work_risk_category,
        next_control_basis=training_record.next_control_basis,
    )
