from datetime import date
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.serialize_training_record_for_audit import serialize_training_record_for_audit
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.update_training_record_row import update_training_record_row
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_training_record_by_id import get_training_record_by_id


# ###### ОНОВЛЕННЯ ЗАПИСУ ІНСТРУКТАЖУ / ОБНОВЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА ######
def update_training_record(
    database_path: Path,
    record_id: int,
    employee_personnel_number: str,
    training_type: str,
    event_date_text: str,
    next_control_date_text: str,
    conducted_by: str,
    note_text: str,
) -> None:
    """Оновлює запис інструктажу, синхронізує сповіщення і пише audit.
    Обновляет запись инструктажа, синхронизирует уведомления и пишет audit.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_training_type = training_type.strip()
    normalized_conducted_by = conducted_by.strip()
    normalized_note = note_text.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_training_type:
        raise ValueError("Потрібно вибрати тип інструктажу.")
    if not normalized_conducted_by:
        raise ValueError("Потрібно вказати, хто проводив інструктаж.")

    event_date = _parse_iso_date(event_date_text)
    next_control_date = _parse_iso_date(next_control_date_text)
    if next_control_date < event_date:
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
            training_type=TrainingType(normalized_training_type),
            event_date=event_date.isoformat(),
            next_control_date=next_control_date.isoformat(),
            conducted_by=normalized_conducted_by,
            note_text=normalized_note,
            status=TrainingStatus.CURRENT,
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


# ###### РОЗБІР ISO-ДАТИ ДЛЯ ОНОВЛЕННЯ ІНСТРУКТАЖУ / РАЗБОР ISO-ДАТЫ ДЛЯ ОБНОВЛЕНИЯ ИНСТРУКТАЖА ######
def _parse_iso_date(date_text: str) -> date:
    """Перетворює текст дати формату РРРР-ММ-ДД у об'єкт date.
    Преобразует текст даты формата ГГГГ-ММ-ДД в объект date.
    """

    normalized_date_text = date_text.strip()
    if not normalized_date_text:
        raise ValueError("Дата обов'язкова у форматі РРРР-ММ-ДД.")
    try:
        return date.fromisoformat(normalized_date_text)
    except ValueError as error:
        raise ValueError("Дата має бути у форматі РРРР-ММ-ДД.") from error
