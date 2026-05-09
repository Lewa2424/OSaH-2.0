from osah.domain.entities.mail_settings import MailSettings
from osah.domain.services.normalize_mail_settings_for_delivery import normalize_mail_settings_for_delivery


# ###### ПЕРЕВІРКА ГОТОВНОСТІ ПОШТОВИХ НАЛАШТУВАНЬ / ПРОВЕРКА ГОТОВНОСТИ ПОЧТОВЫХ НАСТРОЕК ######
def is_mail_settings_ready(mail_settings: MailSettings) -> bool:
    """Повертає True, якщо налаштування містять мінімум для SMTP-відправки.
    Возвращает True, если настройки содержат минимум для SMTP-отправки.
    """

    normalized_mail_settings = normalize_mail_settings_for_delivery(mail_settings)
    return all(
        (
            normalized_mail_settings.smtp_host.strip(),
            normalized_mail_settings.smtp_port > 0,
            normalized_mail_settings.sender_email.strip(),
            normalized_mail_settings.recipient_email.strip(),
        )
    )
