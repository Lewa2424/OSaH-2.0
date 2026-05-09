def build_default_smtp_settings(sender_email: str) -> tuple[str, int, str, bool]:
    """Повертає базові SMTP-параметри за адресою відправника для спрощеного сценарію.
    Returns baseline SMTP settings from sender email for the simplified flow.
    """

    normalized_sender_email = sender_email.strip().lower()
    if "@" not in normalized_sender_email:
        return "", 587, "", True

    domain_name = normalized_sender_email.split("@", maxsplit=1)[1].strip()
    if not domain_name:
        return "", 587, "", True

    return f"smtp.{domain_name}", 587, normalized_sender_email, True
