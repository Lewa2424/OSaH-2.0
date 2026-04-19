from osah.domain.entities.mail_settings import MailSettings


# ###### ПЕРЕВІРКА ГОТОВНОСТІ ПОШТОВИХ НАЛАШТУВАНЬ / ПРОВЕРКА ГОТОВНОСТИ ПОЧТОВЫХ НАСТРОЕК ######
def is_mail_settings_ready(mail_settings: MailSettings) -> bool:
    """Повертає True, якщо налаштування містять мінімум для SMTP-відправки.
    Возвращает True, если настройки содержат минимум для SMTP-отправки.
    """

    return all(
        (
            mail_settings.smtp_host.strip(),
            mail_settings.smtp_port > 0,
            mail_settings.sender_email.strip(),
            mail_settings.recipient_email.strip(),
        )
    )
