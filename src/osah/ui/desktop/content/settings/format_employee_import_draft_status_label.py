from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ ЧЕРНЕТКИ ІМПОРТУ / ФОРМАТИРОВАНИЕ СТАТУСА ЧЕРНОВИКА ИМПОРТА ######
def format_employee_import_draft_status_label(employee_import_draft_status: EmployeeImportDraftStatus) -> str:
    """Повертає локалізовану мітку статусу чернетки імпорту працівника.
    Возвращает локализованную метку статуса черновика импорта сотрудника.
    """

    if employee_import_draft_status == EmployeeImportDraftStatus.NEW:
        return "Новий"
    if employee_import_draft_status == EmployeeImportDraftStatus.UPDATE:
        return "Оновлення"
    if employee_import_draft_status == EmployeeImportDraftStatus.UNCHANGED:
        return "Без змін"
    return "Помилка"
