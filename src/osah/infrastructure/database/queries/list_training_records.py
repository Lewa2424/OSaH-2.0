from sqlite3 import Connection

from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.evaluate_training_status import evaluate_training_status


# ###### ЧТЕНИЕ РЕЕСТРА ИНСТРУКТАЖЕЙ / LIST TRAINING RECORDS ######
def list_training_records(connection: Connection, warning_days: int = 30) -> tuple[TrainingRecord, ...]:
    """Возвращает все записи инструктажей с рассчитанными статусами.
    Returns all training records with calculated statuses.
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
            trainings.note_text,
            trainings.person_category,
            trainings.requires_primary_on_workplace,
            trainings.work_risk_category,
            trainings.next_control_basis
        FROM trainings
        INNER JOIN employees
            ON employees.personnel_number = trainings.employee_personnel_number
        ORDER BY trainings.next_control_date ASC, trainings.id ASC;
        """
    ).fetchall()

    raw_records: list[TrainingRecord] = []
    for row in rows:
        raw_records.append(
            TrainingRecord(
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
        )

    records_by_employee: dict[str, tuple[TrainingRecord, ...]] = {}
    for record in raw_records:
        records_by_employee.setdefault(record.employee_personnel_number, tuple())
        records_by_employee[record.employee_personnel_number] = (
            *records_by_employee[record.employee_personnel_number],
            record,
        )

    return tuple(
        TrainingRecord(
            record_id=record.record_id,
            employee_personnel_number=record.employee_personnel_number,
            employee_full_name=record.employee_full_name,
            training_type=record.training_type,
            event_date=record.event_date,
            next_control_date=record.next_control_date,
            conducted_by=record.conducted_by,
            note_text=record.note_text,
            status=evaluate_training_status(
                record,
                records_by_employee.get(record.employee_personnel_number, (record,)),
                warning_days=warning_days,
            ),
            person_category=record.person_category,
            requires_primary_on_workplace=record.requires_primary_on_workplace,
            work_risk_category=record.work_risk_category,
            next_control_basis=record.next_control_basis,
        )
        for record in raw_records
    )
