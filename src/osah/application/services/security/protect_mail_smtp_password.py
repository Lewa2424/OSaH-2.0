from osah.infrastructure.security.protect_secret_with_windows_dpapi import protect_secret_with_windows_dpapi


# ###### ЗАХИСТ SMTP-ПАРОЛЯ ДЛЯ ЗБЕРЕЖЕННЯ / PROTECT SMTP PASSWORD FOR STORAGE ######
def protect_mail_smtp_password(smtp_password: str) -> str:
    """Повертає значення для збереження в app_settings (DPAPI на Windows).
    Returns a value safe to store in app_settings (DPAPI on Windows).
    """

    if not smtp_password:
        return ""
    try:
        return protect_secret_with_windows_dpapi(smtp_password)
    except OSError:
        return smtp_password
