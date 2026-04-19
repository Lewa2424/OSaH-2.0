from osah.domain.entities.employee import Employee


# ###### ФОРМАТУВАННЯ СТАТУСУ ЗАЙНЯТОСТІ / ФОРМАТИРОВАНИЕ СТАТУСА ЗАНЯТОСТИ ######
def format_employment_status_label(employee: Employee) -> str:
    """Повертає локалізовану мітку статусу зайнятості для UI.
    Возвращает локализованную метку статуса занятости для UI.
    """

    normalized_status = employee.employment_status.strip().lower()
    if normalized_status == "active":
        return "Активний"
    if normalized_status == "archived":
        return "Архівний"
    if not normalized_status:
        return "Не вказано"
    return employee.employment_status
