from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date
from osah.infrastructure.database.commands.insert_training_record import insert_training_record
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### МАСОВЕ СТВОРЕННЯ ІНСТРУКТАЖІВ / CREATE TRAINING RECORDS BATCH ######
def create_training_records_batch(
    database_path: Path,
    employee_personnel_numbers: tuple[str, ...],
    training_type: str,
    event_date_text: str,
    next_control_date_text: str,
    conducted_by: str,
    note_text: str,
    work_risk_category: str = "not_applicable",
    should_update_repeated_control: bool = False,
    use_manual_next_control_date: bool = False,
) -> None:
    """Створює записи інструктажу для кількох працівників одним сценарієм.
    Creates training records for multiple employees in one scenario.
    """

    normalized_personnel_numbers = tuple(
        personnel_number.strip()
        for personnel_number in employee_personnel_numbers
        if personnel_number.strip()
    )
    normalized_training_type = training_type.strip()
    normalized_conducted_by = conducted_by.strip()
    normalized_note = note_text.strip()
    normalized_work_risk_category = work_risk_category.strip() or "not_applicable"
    if not normalized_personnel_numbers:
        raise ValueError("Потрібно вибрати хоча б одного працівника для масового запису.")
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
        TrainingWorkRiskCategory(normalized_work_risk_category),
        manual_next_control_date,
        should_update_repeated_control,
        use_manual_next_control_date,
    )
    if manual_next_control_date is not None and manual_next_control_date < event_date:
        raise ValueError("Дата наступного контролю не може бути раніше дати проведення.")

    connection = create_database_connection(database_path)
    try:
        for personnel_number in normalized_personnel_numbers:
            insert_training_record(
                connection,
                TrainingRecord(
                    record_id=None,
                    employee_personnel_number=personnel_number,
                    employee_full_name="",
                    training_type=training_type_value,
                    event_date=event_date.isoformat(),
                    next_control_date=resolved_next_control_date,
                    conducted_by=normalized_conducted_by,
                    note_text=normalized_note,
                    status=TrainingStatus.CURRENT,
                    work_risk_category=resolved_work_risk_category,
                    next_control_basis=next_control_basis,
                ),
            )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()
