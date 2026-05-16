from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.training_knowledge_check_result import TrainingKnowledgeCheckResult
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_admission_status import TrainingWorkAdmissionStatus
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.find_training_chronology_conflict_reason import find_training_chronology_conflict_reason
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date
from osah.domain.services.serialize_training_record_for_audit import serialize_training_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_training_record_row import update_training_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_training_record_by_id import get_training_record_by_id
from osah.infrastructure.database.queries.list_training_records import list_training_records


# ###### ОБНОВЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА / UPDATE TRAINING RECORD ######
def update_training_record(
    database_path: Path,
    record_id: int,
    employee_personnel_number: str,
    training_type: str,
    event_date_text: str,
    next_control_date_text: str,
    conducted_by: str,
    note_text: str,
    person_category: str = "own_employee",
    requires_primary_on_workplace: bool = True,
    work_risk_category: str = "not_applicable",
    should_update_repeated_control: bool = False,
    use_manual_next_control_date: bool = False,
    knowledge_check_result: str = "legacy_not_tracked",
    work_admission_status: str = "legacy_not_tracked",
    knowledge_check_note: str = "",
    basis_text: str = "",
    basis_note: str = "",
) -> None:
    """Обновляет запись инструктажа, синхронизирует уведомления и пишет audit.
    Updates a training record, synchronizes notifications, and writes audit.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_training_type = training_type.strip()
    normalized_conducted_by = conducted_by.strip()
    normalized_note = note_text.strip()
    normalized_person_category = person_category.strip() or "own_employee"
    normalized_work_risk_category = work_risk_category.strip() or "not_applicable"
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_training_type:
        raise ValueError("Потрібно вибрати тип інструктажу.")
    if not normalized_conducted_by:
        raise ValueError("Потрібно вказати, хто проводив інструктаж.")

    event_date = parse_ui_date_text(event_date_text)
    manual_next_control_date = parse_ui_date_text(next_control_date_text) if next_control_date_text.strip() else None
    training_type_value = TrainingType(normalized_training_type)
    resolved_next_control_date, next_control_basis, resolved_work_risk_category = resolve_training_next_control_date(
        training_type_value,
        event_date,
        TrainingPersonCategory(normalized_person_category),
        requires_primary_on_workplace,
        TrainingWorkRiskCategory(normalized_work_risk_category),
        manual_next_control_date,
        should_update_repeated_control,
        use_manual_next_control_date,
    )
    if manual_next_control_date is not None and manual_next_control_date < event_date:
        raise ValueError("Дата наступного контролю не може бути раніше дати проведення.")

    connection = create_database_connection(database_path)
    try:
        previous_record = get_training_record_by_id(connection, record_id)
        if previous_record is None:
            raise ValueError("Запис інструктажу не знайдено.")

        updated_record = TrainingRecord(
            record_id=record_id,
            employee_personnel_number=normalized_personnel_number,
            employee_full_name=previous_record.employee_full_name,
            training_type=training_type_value,
            event_date=event_date.isoformat(),
            next_control_date=resolved_next_control_date,
            conducted_by=normalized_conducted_by,
            note_text=normalized_note,
            status=TrainingStatus.CURRENT,
            person_category=TrainingPersonCategory(normalized_person_category),
            requires_primary_on_workplace=requires_primary_on_workplace,
            work_risk_category=resolved_work_risk_category,
            next_control_basis=next_control_basis,
            knowledge_check_result=TrainingKnowledgeCheckResult(knowledge_check_result.strip() or "legacy_not_tracked"),
            work_admission_status=TrainingWorkAdmissionStatus(work_admission_status.strip() or "legacy_not_tracked"),
            knowledge_check_note=knowledge_check_note.strip(),
            basis_text=basis_text.strip(),
            basis_note=basis_note.strip(),
            is_current=previous_record.is_current,
            archived_at=previous_record.archived_at,
            archive_reason=previous_record.archive_reason,
            replaced_by_record_id=previous_record.replaced_by_record_id,
            source_module=previous_record.source_module,
            source_record_id=previous_record.source_record_id,
            source_key=previous_record.source_key,
        )
        chronology_conflict_reason = find_training_chronology_conflict_reason(
            updated_record,
            tuple(
                record
                for record in list_training_records(connection)
                if record.employee_personnel_number == normalized_personnel_number
                and record.record_id != record_id
            ),
        )
        if chronology_conflict_reason is not None:
            raise ValueError(chronology_conflict_reason)
        update_training_record_row(connection, updated_record)
        insert_audit_log(
            connection,
            event_type="training.updated",
            module_name="trainings",
            event_level="info",
            actor_name="system",
            entity_name=f"training:{record_id}",
            result_status="success",
            description_text=(
                f"old=({serialize_training_record_for_audit(previous_record)}) "
                f"new=({serialize_training_record_for_audit(updated_record)})"
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
