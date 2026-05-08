from sqlite3 import Connection

from osah.domain.entities.training_knowledge_check_result import TrainingKnowledgeCheckResult
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_admission_status import TrainingWorkAdmissionStatus
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.evaluate_training_status import evaluate_training_status
from osah.infrastructure.database.queries.list_training_records import list_training_records


def get_training_record_by_id(connection: Connection, record_id: int) -> TrainingRecord | None:
    """Повертає одну запис інструктажу за ідентифікатором.
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
            trainings.next_control_basis,
            trainings.knowledge_check_result,
            trainings.work_admission_status,
            trainings.knowledge_check_note,
            trainings.basis_text,
            trainings.basis_note,
            trainings.is_current,
            trainings.archived_at,
            trainings.archive_reason,
            trainings.replaced_by_record_id,
            trainings.source_module,
            trainings.source_record_id,
            trainings.source_key
        FROM trainings
        INNER JOIN employees
            ON employees.personnel_number = trainings.employee_personnel_number
        WHERE trainings.id = ?;
        """,
        (record_id,),
    ).fetchone()
    if row is None:
        return None

    current_employee_records = tuple(
        record
        for record in list_training_records(connection)
        if record.employee_personnel_number == row["employee_personnel_number"]
    )
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
        knowledge_check_result=TrainingKnowledgeCheckResult(row["knowledge_check_result"] or "legacy_not_tracked"),
        work_admission_status=TrainingWorkAdmissionStatus(row["work_admission_status"] or "legacy_not_tracked"),
        knowledge_check_note=row["knowledge_check_note"] or "",
        basis_text=row["basis_text"] or "",
        basis_note=row["basis_note"] or "",
        is_current=bool(int(row["is_current"] or 0)),
        archived_at=row["archived_at"],
        archive_reason=row["archive_reason"] or "",
        replaced_by_record_id=int(row["replaced_by_record_id"]) if row["replaced_by_record_id"] is not None else None,
        source_module=row["source_module"] or "",
        source_record_id=int(row["source_record_id"]) if row["source_record_id"] is not None else None,
        source_key=row["source_key"] or "",
    )
    status = (
        TrainingStatus.CURRENT
        if not training_record.is_current
        else evaluate_training_status(training_record, current_employee_records or (training_record,))
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
        status=status,
        person_category=training_record.person_category,
        requires_primary_on_workplace=training_record.requires_primary_on_workplace,
        work_risk_category=training_record.work_risk_category,
        next_control_basis=training_record.next_control_basis,
        knowledge_check_result=training_record.knowledge_check_result,
        work_admission_status=training_record.work_admission_status,
        knowledge_check_note=training_record.knowledge_check_note,
        basis_text=training_record.basis_text,
        basis_note=training_record.basis_note,
        is_current=training_record.is_current,
        archived_at=training_record.archived_at,
        archive_reason=training_record.archive_reason,
        replaced_by_record_id=training_record.replaced_by_record_id,
        source_module=training_record.source_module,
        source_record_id=training_record.source_record_id,
        source_key=training_record.source_key,
    )
