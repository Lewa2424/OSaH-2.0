from datetime import date
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.infrastructure.database.commands.insert_medical_record import insert_medical_record
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СТВОРЕННЯ МЕДИЧНОГО ЗАПИСУ / СОЗДАНИЕ МЕДИЦИНСКОЙ ЗАПИСИ ######
def create_medical_record(
    database_path: Path,
    employee_personnel_number: str,
    valid_from_text: str,
    valid_until_text: str,
    medical_decision: str,
    restriction_note: str,
) -> None:
    """Створює новий медичний запис і синхронізує контрольні сповіщення.
    Создаёт новую медицинскую запись и синхронизирует контрольные уведомления.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_medical_decision = medical_decision.strip()
    normalized_restriction_note = restriction_note.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_medical_decision:
        raise ValueError("Потрібно вибрати медичне рішення.")

    valid_from = _parse_iso_date(valid_from_text)
    valid_until = _parse_iso_date(valid_until_text)
    if valid_until < valid_from:
        raise ValueError("Дата завершення не може бути раніше дати початку.")

    connection = create_database_connection(database_path)
    try:
        insert_medical_record(
            connection,
            MedicalRecord(
                record_id=None,
                employee_personnel_number=normalized_personnel_number,
                employee_full_name="",
                valid_from=valid_from.isoformat(),
                valid_until=valid_until.isoformat(),
                medical_decision=MedicalDecision(normalized_medical_decision),
                restriction_note=normalized_restriction_note,
                status=MedicalStatus.CURRENT,
            ),
        )
        sync_control_notifications(connection)
        connection.commit()
    finally:
        connection.close()


# ###### РОЗБІР ISO-ДАТИ ДЛЯ МЕДИЦИНИ / РАЗБОР ISO-ДАТЫ ДЛЯ МЕДИЦИНЫ ######
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
