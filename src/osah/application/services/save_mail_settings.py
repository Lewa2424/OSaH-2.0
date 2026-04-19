from pathlib import Path

from osah.domain.entities.mail_settings import MailSettings
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ЗБЕРЕЖЕННЯ ПОШТОВИХ НАЛАШТУВАНЬ / СОХРАНЕНИЕ ПОЧТОВЫХ НАСТРОЕК ######
def save_mail_settings(database_path: Path, mail_settings: MailSettings) -> None:
    """Зберігає налаштування SMTP та параметри щоденного звіту.
    Сохраняет настройки SMTP и параметры ежедневного отчёта.
    """

    connection = create_database_connection(database_path)
    try:
        setting_pairs = {
            "mail.daily_report_enabled": "1" if mail_settings.daily_report_enabled else "0",
            "mail.smtp_host": mail_settings.smtp_host.strip(),
            "mail.smtp_port": str(mail_settings.smtp_port),
            "mail.smtp_username": mail_settings.smtp_username.strip(),
            "mail.smtp_password": mail_settings.smtp_password,
            "mail.sender_email": mail_settings.sender_email.strip(),
            "mail.recipient_email": mail_settings.recipient_email.strip(),
            "mail.use_tls": "1" if mail_settings.use_tls else "0",
            "mail.last_sent_date": mail_settings.last_sent_date.strip(),
        }
        for setting_key, setting_value in setting_pairs.items():
            upsert_app_setting(connection, setting_key, setting_value)
        insert_audit_log(
            connection,
            event_type="mail.settings_updated",
            module_name="reports_mail",
            event_level="info",
            actor_name="system",
            entity_name="mail.settings",
            result_status="success",
            description_text="SMTP settings updated without exposing secrets.",
        )
        connection.commit()
    finally:
        connection.close()
