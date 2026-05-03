from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date
from osah.domain.services.serialize_training_record_for_audit import serialize_training_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_training_record_row import update_training_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_training_record_by_id import get_training_record_by_id


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
        )
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
