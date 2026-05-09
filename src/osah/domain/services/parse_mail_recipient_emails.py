def parse_mail_recipient_emails(recipient_text: str) -> tuple[str, ...]:
    """Повертає нормалізований список email-отримувачів зі строки налаштувань.
    Returns a normalized list of email recipients from the settings string.
    """

    normalized_text = recipient_text.replace("\n", ";").replace(",", ";")
    recipients = tuple(
        token.strip()
        for token in normalized_text.split(";")
        if token.strip()
    )
    return recipients
