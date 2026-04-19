import smtplib
from datetime import datetime
from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.build_daily_report_email_message import build_daily_report_email_message
from osah.application.services.load_mail_settings import load_mail_settings
from osah.application.services.save_daily_report_copy import save_daily_report_copy
from osah.application.services.save_failed_report_email_copy import save_failed_report_email_copy
from osah.application.services.save_mail_settings import save_mail_settings
from osah.domain.entities.mail_settings import MailSettings
from osah.domain.services.is_mail_settings_ready import is_mail_settings_ready
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.logging.log_alert_event import log_alert_event
from osah.infrastructure.logging.log_system_event import log_system_event


# ###### НАДСИЛАННЯ ЩОДЕННОГО ЗВІТУ ПОШТОЮ / ОТПРАВКА ЕЖЕДНЕВНОГО ОТЧЁТА ПО ПОЧТЕ ######
def send_daily_report_email(database_path: Path, attempt_limit: int = 3) -> tuple[Path, Path | None]:
    """Надсилає щоденний звіт поштою, повертає шлях до копії звіту та fallback-листа при невдачі.
    Отправляет ежедневный отчёт по почте, возвращает путь к копии отчёта и fallback-письму при неудаче.
    """

    mail_settings = load_mail_settings(database_path)
    if not is_mail_settings_ready(mail_settings):
        log_alert_event("reports_mail", "Daily report send aborted because mail settings are incomplete.")
        raise ValueError("Поштові налаштування неповні. Спочатку збережіть SMTP-параметри.")

    daily_report_document = build_daily_report_document(database_path)
    report_copy_path = save_daily_report_copy(database_path, daily_report_document)
    email_message = build_daily_report_email_message(daily_report_document, mail_settings)

    last_error: Exception | None = None
    for _ in range(attempt_limit):
        try:
            _send_email_message(mail_settings, email_message)
            updated_mail_settings = MailSettings(
                daily_report_enabled=mail_settings.daily_report_enabled,
                smtp_host=mail_settings.smtp_host,
                smtp_port=mail_settings.smtp_port,
                smtp_username=mail_settings.smtp_username,
                smtp_password=mail_settings.smtp_password,
                sender_email=mail_settings.sender_email,
                recipient_email=mail_settings.recipient_email,
                use_tls=mail_settings.use_tls,
                last_sent_date=datetime.now().strftime("%Y-%m-%d"),
            )
            save_mail_settings(database_path, updated_mail_settings)
            _write_report_delivery_audit_log(
                database_path,
                event_type="report.sent",
                result_status="success",
                description_text=f"report_copy={report_copy_path.name}",
            )
            log_system_event("reports_mail", f"Daily report sent successfully: copy={report_copy_path.name}")
            return report_copy_path, None
        except Exception as error:  # noqa: BLE001
            last_error = error

    failed_email_copy_path = save_failed_report_email_copy(
        database_path,
        email_message,
        datetime.now().strftime("%Y%m%d-%H%M%S"),
    )
    _write_report_delivery_audit_log(
        database_path,
        event_type="report.failed",
        result_status="failed",
        description_text=f"fallback_copy={failed_email_copy_path.name};error={type(last_error).__name__ if last_error else 'unknown'}",
    )
    log_alert_event(
        "reports_mail",
        f"Daily report send failed after retries: fallback_copy={failed_email_copy_path.name};error={type(last_error).__name__ if last_error else 'unknown'}",
    )
    return report_copy_path, failed_email_copy_path


# ###### SMTP-НАДСИЛАННЯ EMAIL-ПОВІДОМЛЕННЯ / SMTP-ОТПРАВКА EMAIL-СООБЩЕНИЯ ######
def _send_email_message(mail_settings: MailSettings, email_message) -> None:
    """Відправляє email-повідомлення через SMTP із заданими налаштуваннями.
    Отправляет email-сообщение через SMTP с заданными настройками.
    """

    with smtplib.SMTP(mail_settings.smtp_host, mail_settings.smtp_port, timeout=20) as smtp_client:
        if mail_settings.use_tls:
            smtp_client.starttls()
        if mail_settings.smtp_username.strip():
            smtp_client.login(mail_settings.smtp_username, mail_settings.smtp_password)
        smtp_client.send_message(email_message)


# ###### ЗАПИС AUDIT-ПОДІЇ ДОСТАВКИ ЗВІТУ / ЗАПИСЬ AUDIT-СОБЫТИЯ ДОСТАВКИ ОТЧЁТА ######
def _write_report_delivery_audit_log(
    database_path: Path,
    event_type: str,
    result_status: str,
    description_text: str,
) -> None:
    """Зберігає audit-подію доставки або недоставки щоденного звіту.
    Сохраняет audit-событие доставки или недоставки ежедневного отчёта.
    """

    connection = create_database_connection(database_path)
    try:
        insert_audit_log(
            connection,
            event_type=event_type,
            module_name="reports_mail",
            event_level="warning" if result_status != "success" else "info",
            actor_name="system",
            entity_name="daily_report",
            result_status=result_status,
            description_text=description_text,
        )
        connection.commit()
    finally:
        connection.close()
