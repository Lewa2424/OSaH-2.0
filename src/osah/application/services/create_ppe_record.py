from datetime import date
from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.infrastructure.database.commands.insert_ppe_record import insert_ppe_record
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### СТВОРЕННЯ ЗАПИСУ ЗІЗ / СОЗДАНИЕ ЗАПИСИ СИЗ ######
def create_ppe_record(
    database_path: Path,
    employee_personnel_number: str,
    ppe_name: str,
    is_required: bool,
    is_issued: bool,
    issue_date_text: str,
    replacement_date_text: str,
    quantity_text: str,
    note_text: str,
) -> None:
    """Створює новий запис ЗІЗ та синхронізує контрольні сповіщення.
    Создаёт новую запись СИЗ и синхронизирует контрольные уведомления.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_ppe_name = ppe_name.strip()
    normalized_quantity_text = quantity_text.strip()
    normalized_note = note_text.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_ppe_name:
        raise ValueError("Потрібно вказати назву ЗІЗ.")
    if not normalized_quantity_text:
        raise ValueError("Потрібно вказати кількість.")

    quantity = _parse_quantity(normalized_quantity_text)
    issue_date = _parse_iso_date(issue_date_text)
    replacement_date = _parse_iso_date(replacement_date_text)
    if replacement_date < issue_date:
        raise ValueError("Дата заміни не може бути раніше дати видачі.")

    connection = create_database_connection(database_path)
    try:
        insert_ppe_record(
            connection,
            PpeRecord(
                record_id=None,
                employee_personnel_number=normalized_personnel_number,
                employee_full_name="",
                ppe_name=normalized_ppe_name,
                is_required=is_required,
                is_issued=is_issued,
                issue_date=issue_date.isoformat(),
                replacement_date=replacement_date.isoformat(),
                quantity=quantity,
                note_text=normalized_note,
                status=PpeStatus.CURRENT,
            ),
        )
        sync_control_notifications(connection)
    finally:
        connection.close()


# ###### РОЗБІР ISO-ДАТИ ДЛЯ ЗІЗ / РАЗБОР ISO-ДАТЫ ДЛЯ СИЗ ######
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


# ###### РОЗБІР КІЛЬКОСТІ ЗІЗ / РАЗБОР КОЛИЧЕСТВА СИЗ ######
def _parse_quantity(quantity_text: str) -> int:
    """Перетворює текст кількості у додатне ціле число.
    Преобразует текст количества в положительное целое число.
    """

    try:
        quantity = int(quantity_text)
    except ValueError as error:
        raise ValueError("Кількість має бути цілим числом.") from error
    if quantity <= 0:
        raise ValueError("Кількість має бути більшою за нуль.")
    return quantity
