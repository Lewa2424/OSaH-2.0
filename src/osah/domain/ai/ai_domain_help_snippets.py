from osah.domain.entities.ai_ui_context import AiUiContext


_DOMAIN_SNIPPETS: dict[str, str] = {
    "targeted_training": "Цільовий інструктаж проводять перед конкретними роботами з підвищеним ризиком або за нарядом-допуском.",
    "repeated_training": "Повторний інструктаж підтверджує знання вимог охорони праці на робочому місці.",
    "work_permit": "Наряд-допуск — документ, що дозволяє виконання робіт підвищеної небезпеки з переліком учасників і заходів.",
    "ppe_replacement_date": "Дата заміни ЗІЗ — строк, до якого засіб має бути замінений або перевірений.",
    "medical_restriction": "Обмеження медогляду означає, що працівник допущений не до всіх видів робіт.",
    "port_r_passport": "Паспорт ділянки PORT-R фіксує ризики, умови робіт і заходи з їх зменшення.",
    "port_r_gaps": "Прогалини PORT-R — незаповнені поля паспорта або критичний профіль ризику без заходів.",
    "work_permit_readiness": "Готовність учасників наряду залежить від інструктажів, медогляду та ЗІЗ кожного працівника.",
}

_ERROR_SNIPPETS: dict[str, str] = {
    "employee_not_found": "Якщо працівника не знайдено — перевірте ПІБ або табельний номер у реєстрі.",
    "ambiguous_employee": "Якщо знайдено кілька збігів — оберіть потрібного зі списку в AI-панелі.",
    "invalid_date": "Дати вводьте у форматі ДД.ММ.РРРР або словами «сьогодні», «завтра».",
    "save_failed": "Якщо запис не збережено — перевірте обов'язкові поля та права доступу.",
    "bulk_unsupported": "Масові дії через AI поки не підтримуються. Виконуйте їх у реєстрі або для одного працівника.",
}


def get_ai_domain_help_snippet(topic_key: str) -> str | None:
    """Повертає статичне пояснення доменного терміну.
    Returns a static domain term explanation snippet.
    """

    normalized = topic_key.strip().lower()
    for key, snippet in _DOMAIN_SNIPPETS.items():
        if key in normalized or normalized in key:
            return snippet
    if "цільов" in normalized or "целев" in normalized:
        return _DOMAIN_SNIPPETS["targeted_training"]
    if "повтор" in normalized:
        return _DOMAIN_SNIPPETS["repeated_training"]
    if "наряд" in normalized:
        return _DOMAIN_SNIPPETS["work_permit"]
    if "port" in normalized or "паспорт" in normalized:
        return _DOMAIN_SNIPPETS["port_r_passport"]
    return None


def get_ai_error_help_snippet(error_key: str) -> str | None:
    """Повертає playbook-пояснення типової помилки.
    Returns an error playbook explanation snippet.
    """

    return _ERROR_SNIPPETS.get(error_key.strip().lower())
