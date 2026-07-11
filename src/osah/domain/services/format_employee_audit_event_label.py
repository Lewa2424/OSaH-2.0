_EMPLOYEE_AUDIT_EVENT_LABELS: dict[str, str] = {
    "employee.created": "Картку створено",
    "employee.updated": "Картку оновлено",
    "employee.archived": "Переміщено в архів",
    "employee.reactivated": "Повернено з архіву",
    "training.created": "Інструктаж створено",
    "training.updated": "Інструктаж оновлено",
    "training.deleted": "Інструктаж видалено",
    "training.replaced": "Інструктаж замінено",
    "training.archived": "Інструктаж архівовано",
    "training.created_from_work_permit": "Інструктаж створено з наряду",
    "training.updated_from_work_permit": "Інструктаж оновлено з наряду",
    "ppe.created": "Запис ЗІЗ створено",
    "ppe.updated": "Запис ЗІЗ оновлено",
    "medical.created": "Медичний запис створено",
    "medical.updated": "Медичний запис оновлено",
    "work_permit.created": "Наряд створено",
    "work_permit.updated": "Наряд оновлено",
    "work_permit.closed": "Наряд закрито",
    "work_permit.canceled": "Наряд скасовано",
    "work_permit.extended": "Строк наряду продовжено",
    "work_permit.reissued": "Наряд перевипущено",
    "work_permit.participants_changed": "Учасників наряду змінено",
    "work_permit.daily_check_recorded": "Щоденну перевірку наряду зафіксовано",
}


# ###### ПІДПИС ПОДІЇ AUDIT / FORMAT EMPLOYEE AUDIT EVENT LABEL ######
def format_employee_audit_event_label(event_type: str) -> str:
    """Повертає зрозумілу українську назву audit-події для картки працівника.
    Returns a readable Ukrainian label for an employee audit event.
    """

    normalized_event_type = event_type.strip()
    if not normalized_event_type:
        return "Подія"
    return _EMPLOYEE_AUDIT_EVENT_LABELS.get(normalized_event_type, normalized_event_type)
