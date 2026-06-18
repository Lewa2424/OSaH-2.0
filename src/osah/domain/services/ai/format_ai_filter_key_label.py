"""Локалізовані підписи filter_key для AI-відповідей.
Localized filter_key labels for AI query answers.
"""


def format_ai_filter_key_label(filter_key: str | None) -> str:
    """Повертає український підпис статусу замість канонічного filter_key.
    Returns a Ukrainian status label instead of a canonical filter_key.
    """

    normalized = (filter_key or "").strip().lower()
    labels = {
        "warning": "Увага",
        "critical": "Критично",
        "overdue": "Прострочено",
        "missing": "Відсутній",
        "not_issued": "Не видано",
        "restricted": "Обмежено",
        "active": "Активні",
        "slinger": "Стропальники",
    }
    return labels.get(normalized, normalized or "статус")
