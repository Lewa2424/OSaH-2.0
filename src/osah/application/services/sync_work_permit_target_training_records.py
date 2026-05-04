from dataclasses import replace
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
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_training_record import insert_training_record
from osah.infrastructure.database.commands.update_training_record_row import update_training_record_row


def sync_work_permit_target_training_records(
    connection: Connection,
    work_permit_record: WorkPermitRecord,
) -> None:
    """Синхронізує цільові інструктажі учасників із картки наряду-допуску.
    Synchronizes participant targeted-training records from a work-permit card.
    """

    normalized_status = normalize_work_permit_target_training_status(work_permit_record.target_training_status)
    if normalized_status not in {
        WorkPermitTargetTrainingStatus.DONE_PASSED,
        WorkPermitTargetTrainingStatus.DONE_FAILED,
    }:
        return

    for participant in work_permit_record.participants:
        source_key = _build_source_key(work_permit_record, participant.employee_personnel_number)
        training_record = _build_training_record(
            connection,
            work_permit_record,
            participant.employee_personnel_number,
            source_key,
            normalized_status,
        )
        existing_record_id = _find_training_record_id_by_source_key(connection, source_key)
        if existing_record_id is None:
            created_record_id = insert_training_record(connection, training_record)
            created_record = replace(training_record, record_id=created_record_id)
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
                    created_record,
                ),
            )
            continue

        previous_snapshot = connection.execute(
            """
            SELECT
                employee_personnel_number,
                training_type,
                event_date,
                next_control_date,
                conducted_by,
                note_text,
                person_category,
                requires_primary_on_workplace,
                work_risk_category,
                next_control_basis,
                knowledge_check_result,
                work_admission_status,
                knowledge_check_note,
                basis_text,
                basis_note,
                source_module,
                source_record_id,
                source_key
            FROM trainings
            WHERE id = ?;
            """,
            (existing_record_id,),
        ).fetchone()
        updated_record = replace(training_record, record_id=existing_record_id)
        update_training_record_row(connection, updated_record)
        before_text = _serialize_training_row(previous_snapshot, existing_record_id)
        insert_audit_log(
            connection,
            event_type="training.updated_from_work_permit",
            module_name="trainings",
            event_level="info",
            actor_name="system",
            entity_name=f"training:{participant.employee_personnel_number}:work_permit:{work_permit_record.permit_number}",
            result_status="success",
            description_text=(
                f"before=({before_text}); "
                f"after=({_build_audit_description(participant.employee_personnel_number, work_permit_record, normalized_status, updated_record)})"
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
        record_id=None,
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
        source_module="work_permits",
        source_record_id=work_permit_record.record_id,
        source_key=source_key,
    )


def _find_training_record_id_by_source_key(connection: Connection, source_key: str) -> int | None:
    row = connection.execute(
        "SELECT id FROM trainings WHERE source_key = ? LIMIT 1;",
        (source_key,),
    ).fetchone()
    return int(row["id"]) if row is not None else None


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


def _serialize_training_row(row, record_id: int) -> str:
    if row is None:
        return ""
    return (
        f"id={record_id}; "
        f"employee={row['employee_personnel_number']}; "
        f"type={row['training_type']}; "
        f"event_date={row['event_date']}; "
        f"next_control={row['next_control_date']}; "
        f"person_category={row['person_category']}; "
        f"requires_primary={int(row['requires_primary_on_workplace'] or 0)}; "
        f"risk={row['work_risk_category']}; "
        f"basis={row['next_control_basis']}; "
        f"knowledge_result={row['knowledge_check_result']}; "
        f"admission={row['work_admission_status']}; "
        f"knowledge_note={row['knowledge_check_note']}; "
        f"basis_text={row['basis_text']}; "
        f"basis_note={row['basis_note']}; "
        f"source_module={row['source_module']}; "
        f"source_record_id={row['source_record_id'] or ''}; "
        f"source_key={row['source_key']}; "
        f"conducted_by={row['conducted_by']}; "
        f"note={row['note_text']}"
    )
