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


def list_training_records(
    connection: Connection,
    warning_days: int = 30,
    include_archived: bool = False,
) -> tuple[TrainingRecord, ...]:
    """Повертає записи інструктажів з новими полями та розрахованими статусами.
    Returns training records with new fields and calculated statuses.
    """

    rows = connection.execute(
        f"""
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
        {'WHERE trainings.is_current = 1' if not include_archived else ''}
        ORDER BY trainings.next_control_date ASC, trainings.event_date DESC, trainings.id DESC;
        """
    ).fetchall()

    raw_records: list[TrainingRecord] = [_build_training_record(row) for row in rows]

    current_records_by_employee: dict[str, tuple[TrainingRecord, ...]] = {}
    for record in raw_records:
        if not record.is_current:
            continue
        current_records_by_employee.setdefault(record.employee_personnel_number, tuple())
        current_records_by_employee[record.employee_personnel_number] = (
            *current_records_by_employee[record.employee_personnel_number],
            record,
        )

    return tuple(
        _build_evaluated_training_record(record, current_records_by_employee, warning_days)
        for record in raw_records
    )


def _build_training_record(row) -> TrainingRecord:
    return TrainingRecord(
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


def _build_evaluated_training_record(
    record: TrainingRecord,
    current_records_by_employee: dict[str, tuple[TrainingRecord, ...]],
    warning_days: int,
) -> TrainingRecord:
    if not record.is_current:
        status = TrainingStatus.CURRENT
    else:
        status = evaluate_training_status(
            record,
            current_records_by_employee.get(record.employee_personnel_number, (record,)),
            warning_days=warning_days,
        )
    return TrainingRecord(
        record_id=record.record_id,
        employee_personnel_number=record.employee_personnel_number,
        employee_full_name=record.employee_full_name,
        training_type=record.training_type,
        event_date=record.event_date,
        next_control_date=record.next_control_date,
        conducted_by=record.conducted_by,
        note_text=record.note_text,
        status=status,
        person_category=record.person_category,
        requires_primary_on_workplace=record.requires_primary_on_workplace,
        work_risk_category=record.work_risk_category,
        next_control_basis=record.next_control_basis,
        knowledge_check_result=record.knowledge_check_result,
        work_admission_status=record.work_admission_status,
        knowledge_check_note=record.knowledge_check_note,
        basis_text=record.basis_text,
        basis_note=record.basis_note,
        is_current=record.is_current,
        archived_at=record.archived_at,
        archive_reason=record.archive_reason,
        replaced_by_record_id=record.replaced_by_record_id,
        source_module=record.source_module,
        source_record_id=record.source_record_id,
        source_key=record.source_key,
    )
