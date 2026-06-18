def build_registry_suggestion_clarification_message(query: str, *, label: str) -> str:
    """Формує текст уточнення «ви мали на увазі» для сутності реєстру.
    Builds a did-you-mean clarification message for a registry entity.
    """

    normalized_query = query.strip()
    if not normalized_query:
        return f"Уточніть {label}."
    return f"«{normalized_query}» не знайдено в реєстрі ({label}). Ви мали на увазі:"


def build_registry_not_found_clarification_message(query: str, *, label: str) -> str:
    """Формує текст, коли збігів у реєстрі немає навіть серед близьких.
    Builds a message when no close registry matches were found.
    """

    normalized_query = query.strip()
    if not normalized_query:
        return f"Уточніть {label}."
    return (
        f"«{normalized_query}» не знайдено в реєстрі ({label}). "
        "Перефразуйте назву або оберіть підрозділ/посаду з реєстру."
    )
