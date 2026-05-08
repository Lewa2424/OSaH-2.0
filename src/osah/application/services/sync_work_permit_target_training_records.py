from sqlite3 import Connection

from osah.domain.entities.training_knowledge_check_result import TrainingKnowledgeCheckResult
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_admission_status import TrainingWorkAdmissionStatus
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_target_training_status import WorkPermitTargetTrainingStatus
from osah.domain.services.normalize_work_permit_target_training_status import normalize_work_permit_target_training_status
from osah.domain.services.serialize_training_record_for_audit import serialize_training_record_for_audit
from osah.infrastructure.database.commands.archive_training_record_row import archive_training_record_row
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_training_record import insert_training_record
from osah.infrastructure.database.commands.update_training_record_row import update_training_record_row
from osah.infrastructure.database.queries.get_training_record_by_id import get_training_record_by_id


def sync_work_permit_target_training_records(
    connection: Connection,
    work_permit_record: WorkPermitRecord,
) -> None:
    """Синхронізує цільові інструктажі учасників із картки наряду-допуску.
    Synchronizes participant targeted-training records from a work-permit card.
    """

    normalized_status = normalize_work_permit_target_training_status(work_permit_record.target_training_status)
    linked_records = _load_linked_training_records(connection, work_permit_record.record_id)
    linked_by_source_key = {record.source_key: record for record in linked_records if record.source_key}
    desired_source_keys = {
        _build_source_key(work_permit_record, participant.employee_personnel_number)
        for participant in work_permit_record.participants
    }

    if normalized_status not in {
        WorkPermitTargetTrainingStatus.DONE_PASSED,
        WorkPermitTargetTrainingStatus.DONE_FAILED,
    }:
        for linked_record in linked_records:
            _archive_linked_record(connection, linked_record, work_permit_record, normalized_status)
        return

    for linked_record in linked_records:
        if linked_record.source_key not in desired_source_keys:
            _archive_linked_record(connection, linked_record, work_permit_record, normalized_status)

    for participant in work_permit_record.participants:
        source_key = _build_source_key(work_permit_record, participant.employee_personnel_number)
        existing_record = linked_by_source_key.get(source_key)
        training_record = _build_training_record(
            connection,
            work_permit_record,
            participant.employee_personnel_number,
            source_key,
            normalized_status,
            existing_record,
        )
        if existing_record is None:
            created_record_id = insert_training_record(connection, training_record)
            created_record = get_training_record_by_id(connection, created_record_id)
            insert_audit_log(
                connection,
                event_type="training.created_from_work_permit",
                module_name="trainings",
                event_level="info",
                actor_name="system",
                entity_name=f"training:{participant.employee_personnel_number}:work_permit:{work_permit_record.permit_number}",
                result_status="success",
                description_text=_build_audit_description(
                    participant.employee_personnel_number,
                    work_permit_record,
                    normalized_status,
                    created_record or training_record,
                ),
            )
            continue

        update_training_record_row(connection, training_record)
        insert_audit_log(
            connection,
            event_type="training.updated_from_work_permit",
            module_name="trainings",
            event_level="info",
            actor_name="system",
            entity_name=f"training:{participant.employee_personnel_number}:work_permit:{work_permit_record.permit_number}",
            result_status="success",
            description_text=(
                f"before=({serialize_training_record_for_audit(existing_record)}); "
                f"after=({_build_audit_description(participant.employee_personnel_number, work_permit_record, normalized_status, training_record)})"
            ),
        )


def _load_linked_training_records(connection: Connection, source_record_id: int | None) -> tuple[TrainingRecord, ...]:
    if source_record_id is None:
        return ()
    rows = connection.execute(
        """
        SELECT id
        FROM trainings
        WHERE source_module = 'work_permits' AND source_record_id = ?
        ORDER BY id ASC;
        """,
        (source_record_id,),
    ).fetchall()
    records: list[TrainingRecord] = []
    for row in rows:
        record = get_training_record_by_id(connection, int(row["id"]))
        if record is not None:
            records.append(record)
    return tuple(records)


def _archive_linked_record(
    connection: Connection,
    linked_record: TrainingRecord,
    work_permit_record: WorkPermitRecord,
    normalized_status: WorkPermitTargetTrainingStatus,
) -> None:
    if not linked_record.is_current:
        return
    archive_training_record_row(
        connection,
        int(linked_record.record_id),
        archive_reason="replaced_by_work_permit_target_training",
        replaced_by_record_id=None,
    )
    insert_audit_log(
        connection,
        event_type="training.archived",
        module_name="trainings",
        event_level="warning",
        actor_name="system",
        entity_name=f"training:{linked_record.employee_personnel_number}:work_permit:{work_permit_record.permit_number}",
        result_status="success",
        description_text=(
            f"employee_personnel_number={linked_record.employee_personnel_number}; "
            f"training_type=targeted; "
            f"old_record_id={linked_record.record_id}; "
            f"new_record_id=; "
            f"archive_reason=replaced_by_work_permit_target_training; "
            f"target_status={normalized_status.value}; "
            f"old=({serialize_training_record_for_audit(linked_record)})"
        ),
    )


def _build_source_key(work_permit_record: WorkPermitRecord, employee_personnel_number: str) -> str:
    return f"work_permit_target_training:{work_permit_record.record_id}:{employee_personnel_number}"


def _build_training_record(
    connection: Connection,
    work_permit_record: WorkPermitRecord,
    employee_personnel_number: str,
    source_key: str,
    normalized_status: WorkPermitTargetTrainingStatus,
    existing_record: TrainingRecord | None,
) -> TrainingRecord:
    employee_row = connection.execute(
        "SELECT full_name FROM employees WHERE personnel_number = ?;",
        (employee_personnel_number,),
    ).fetchone()
    employee_full_name = str(employee_row["full_name"]) if employee_row is not None else ""
    is_passed = normalized_status == WorkPermitTargetTrainingStatus.DONE_PASSED
    note_text = (
        f"Цільовий інструктаж за нарядом-допуском {work_permit_record.permit_number}. "
        f"Вид робіт: {work_permit_record.work_kind}. "
        f"Причина: виконання робіт за нарядом-допуском."
    )
    knowledge_check_note = (
        "Перевірка знань/навичок за цільовим інструктажем пройдена."
        if is_passed
        else "Перевірка знань/навичок за цільовим інструктажем не пройдена. Допуск до робіт заборонено."
    )
    basis_note = work_permit_record.target_training_note.strip() or "Цільовий інструктаж створено автоматично з картки наряду-допуску."
    return TrainingRecord(
        record_id=existing_record.record_id if existing_record is not None else None,
        employee_personnel_number=employee_personnel_number,
        employee_full_name=employee_full_name,
        training_type=TrainingType.TARGETED,
        event_date=work_permit_record.target_training_date,
        next_control_date="",
        conducted_by=work_permit_record.target_training_conducted_by,
        note_text=note_text,
        status=TrainingStatus.CURRENT,
        person_category=TrainingPersonCategory.OWN_EMPLOYEE,
        requires_primary_on_workplace=False,
        work_risk_category=TrainingWorkRiskCategory.NOT_APPLICABLE,
        next_control_basis=TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL,
        knowledge_check_result=(
            TrainingKnowledgeCheckResult.SATISFACTORY
            if is_passed
            else TrainingKnowledgeCheckResult.UNSATISFACTORY
        ),
        work_admission_status=(
            TrainingWorkAdmissionStatus.ALLOWED
            if is_passed
            else TrainingWorkAdmissionStatus.NOT_ALLOWED
        ),
        knowledge_check_note=knowledge_check_note,
        basis_text=f"Наряд-допуск {work_permit_record.permit_number}",
        basis_note=basis_note,
        is_current=True,
        archived_at=None,
        archive_reason="",
        replaced_by_record_id=None,
        source_module="work_permits",
        source_record_id=work_permit_record.record_id,
        source_key=source_key,
    )


def _build_audit_description(
    employee_personnel_number: str,
    work_permit_record: WorkPermitRecord,
    normalized_status: WorkPermitTargetTrainingStatus,
    training_record: TrainingRecord,
) -> str:
    return (
        f"permit={work_permit_record.permit_number}; "
        f"employee={employee_personnel_number}; "
        f"target_status={normalized_status.value}; "
        f"target_date={work_permit_record.target_training_date}; "
        f"knowledge_result={training_record.knowledge_check_result.value}; "
        f"admission={training_record.work_admission_status.value}; "
        f"training=({serialize_training_record_for_audit(training_record)})"
    )
