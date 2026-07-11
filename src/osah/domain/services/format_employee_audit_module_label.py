_EMPLOYEE_AUDIT_MODULE_LABELS: dict[str, str] = {
    "employees": "Працівники",
    "archive": "Архів",
    "trainings": "Інструктажі",
    "ppe": "ЗІЗ",
    "medical": "Медицина",
    "work_permits": "Наряди-допуски",
}


# ###### ПІДПИС МОДУЛЯ AUDIT / FORMAT EMPLOYEE AUDIT MODULE LABEL ######
def format_employee_audit_module_label(module_name: str) -> str:
    """Повертає локалізовану назву модуля для audit-запису.
    Returns a localized module name for an audit entry.
    """

    normalized_module_name = module_name.strip()
    if not normalized_module_name:
        return "Модуль"
    return _EMPLOYEE_AUDIT_MODULE_LABELS.get(normalized_module_name, normalized_module_name)
