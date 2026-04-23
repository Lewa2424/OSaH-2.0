import re


_SENSITIVE_WORD_PATTERNS = (
    "password",
    "пароль",
    "secret",
    "token",
    "recovery",
    "service_code",
    "service-code",
    "smtp_password",
    "hash",
    "salt",
)


# ###### МАСКУВАННЯ СЕКРЕТІВ У ЛОГАХ / LOG SECRET REDACTION ######
def sanitize_log_message(message_text: str) -> str:
    """Маскує секрети та чутливі значення перед записом у системні або audit-логи.
    Redacts secrets and sensitive values before writing system or audit logs.
    """

    sanitized_text = str(message_text)
    for sensitive_word in _SENSITIVE_WORD_PATTERNS:
        sanitized_text = re.sub(
            rf"({re.escape(sensitive_word)}\s*[:=]\s*)[^;\s,)\]]+",
            rf"\1[REDACTED]",
            sanitized_text,
            flags=re.IGNORECASE,
        )
    return sanitized_text


# ###### ПЕРЕВІРКА ТЕКСТУ НА СЕКРЕТИ / SECRET TEXT CHECK ######
def contains_sensitive_marker(message_text: str) -> bool:
    """Повертає True, якщо текст містить маркер потенційно чутливого поля.
    Returns True when text contains a potentially sensitive field marker.
    """

    lowered_text = str(message_text).lower()
    return any(sensitive_word in lowered_text for sensitive_word in _SENSITIVE_WORD_PATTERNS)
