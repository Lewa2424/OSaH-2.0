from osah.infrastructure.security.protect_secret_with_windows_dpapi import unprotect_secret_with_windows_dpapi


# ###### РОЗШИФРУВАННЯ SMTP-ПАРОЛЯ / UNPROTECT SMTP PASSWORD ######
def unprotect_mail_smtp_password(stored_password: str) -> str:
    """Повертає SMTP-пароль для UI та відправки листа.
    Returns SMTP password for UI and mail delivery.
    """

    if not stored_password:
        return ""
    if stored_password.startswith("dpapi:v1:"):
        return unprotect_secret_with_windows_dpapi(stored_password)
    return stored_password
