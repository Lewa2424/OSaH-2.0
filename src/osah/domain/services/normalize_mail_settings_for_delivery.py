from osah.domain.entities.mail_settings import MailSettings
from osah.domain.services.build_default_smtp_settings import build_default_smtp_settings


# ###### НОРМАЛІЗАЦІЯ ПОШТОВИХ НАЛАШТУВАНЬ ДЛЯ ДОСТАВКИ / НОРМАЛИЗАЦИЯ ПОЧТОВЫХ НАСТРОЕК ДЛЯ ДОСТАВКИ ######
def normalize_mail_settings_for_delivery(mail_settings: MailSettings) -> MailSettings:
    """Повертає MailSettings з підставленими базовими SMTP-значеннями, якщо вони не задані явно.
    Returns MailSettings with baseline SMTP values filled in when they are not explicitly provided.
    """

    default_host, default_port, default_username, default_tls = build_default_smtp_settings(mail_settings.sender_email)
    return MailSettings(
        daily_report_enabled=mail_settings.daily_report_enabled,
        smtp_host=mail_settings.smtp_host.strip() or default_host,
        smtp_port=mail_settings.smtp_port if mail_settings.smtp_port > 0 else default_port,
        smtp_username=mail_settings.smtp_username.strip() or default_username,
        smtp_password=mail_settings.smtp_password,
        sender_email=mail_settings.sender_email.strip(),
        recipient_email=mail_settings.recipient_email.strip(),
        use_tls=mail_settings.use_tls if mail_settings.smtp_host.strip() else default_tls,
        last_sent_date=mail_settings.last_sent_date.strip(),
        daily_report_time=mail_settings.daily_report_time.strip() or "08:00",
    )
