from pathlib import Path

from osah.domain.entities.mail_settings import MailSettings
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


# ###### ЗАВАНТАЖЕННЯ ПОШТОВИХ НАЛАШТУВАНЬ / ЗАГРУЗКА ПОЧТОВЫХ НАСТРОЕК ######
def load_mail_settings(database_path: Path) -> MailSettings:
    """Повертає збережені поштові налаштування або їхні безпечні значення за замовчуванням.
    Возвращает сохранённые почтовые настройки или их безопасные значения по умолчанию.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    return MailSettings(
        daily_report_enabled=app_settings.get("mail.daily_report_enabled", "0") == "1",
        smtp_host=app_settings.get("mail.smtp_host", ""),
        smtp_port=int(app_settings.get("mail.smtp_port", "587") or "587"),
        smtp_username=app_settings.get("mail.smtp_username", ""),
        smtp_password=app_settings.get("mail.smtp_password", ""),
        sender_email=app_settings.get("mail.sender_email", ""),
        recipient_email=app_settings.get("mail.recipient_email", ""),
        use_tls=app_settings.get("mail.use_tls", "1") == "1",
        last_sent_date=app_settings.get("mail.last_sent_date", ""),
    )
