from email.message import EmailMessage
from pathlib import Path


# ###### ЗБЕРЕЖЕННЯ НЕВІДПРАВЛЕНОГО ЛИСТА ЗВІТУ / СОХРАНЕНИЕ НЕОТПРАВЛЕННОГО ПИСЬМА ОТЧЁТА ######
def save_failed_report_email_copy(database_path: Path, email_message: EmailMessage, file_name_suffix: str) -> Path:
    """Зберігає невідправлений лист у форматі EML для ручного надсилання.
    Сохраняет неотправленное письмо в формате EML для ручной отправки.
    """

    outbox_directory = database_path.parent / "reports" / "outbox"
    outbox_directory.mkdir(parents=True, exist_ok=True)
    outbox_file_path = outbox_directory / f"daily-report-{file_name_suffix}.eml"
    outbox_file_path.write_text(email_message.as_string(), encoding="utf-8")
    return outbox_file_path
