from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ ЧЕРНЕТКИ ІМПОРТУ / FORMAT IMPORT DRAFT STATUS LABEL ######
def format_employee_import_draft_status_label(employee_import_draft_status: EmployeeImportDraftStatus) -> str:
    """Повертає локалізовану мітку статусу чернетки імпорту працівника.
    Returns a localized label for an employee import draft status.
    """

    if employee_import_draft_status == EmployeeImportDraftStatus.NEW:
        return "Новий"
    if employee_import_draft_status == EmployeeImportDraftStatus.UPDATE:
        return "Оновлення"
    if employee_import_draft_status == EmployeeImportDraftStatus.UNCHANGED:
        return "Без змін"
    return "Помилка"
