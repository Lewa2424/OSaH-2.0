from osah.domain.entities.employee import Employee
from osah.domain.entities.employee_import_draft import EmployeeImportDraft
from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus
from osah.domain.services.normalize_import_employment_status import normalize_import_employment_status


# ###### ПОБУДОВА ЧЕРНЕТКИ ІМПОРТУ ПРАЦІВНИКА / ПОСТРОЕНИЕ ЧЕРНОВИКА ИМПОРТА СОТРУДНИКА ######
def build_employee_import_draft(
    batch_id: int,
    source_row_number: int,
    row_data: dict[str, str],
    existing_employees_by_number: dict[str, Employee],
) -> EmployeeImportDraft:
    """Повертає валідовану чернетку імпорту працівника на основі рядка джерела.
    Возвращает валидированный черновик импорта сотрудника на основе строки источника.
    """

    personnel_number = row_data.get("personnel_number", "").strip()
    full_name = row_data.get("full_name", "").strip()
    position_name = row_data.get("position_name", "").strip()
    department_name = row_data.get("department_name", "").strip()
    employment_status = normalize_import_employment_status(row_data.get("employment_status", ""))

    issue_messages: list[str] = []
    if not personnel_number:
        issue_messages.append("Не вказано табельний номер")
    if not full_name:
        issue_messages.append("Не вказано ПІБ")
    if not position_name:
        issue_messages.append("Не вказано посаду")
    if not department_name:
        issue_messages.append("Не вказано підрозділ")
    if not employment_status:
        issue_messages.append("Не вказано коректний статус зайнятості")

    existing_employee = existing_employees_by_number.get(personnel_number)
    if issue_messages:
        resolution_status = EmployeeImportDraftStatus.INVALID
    elif existing_employee is None:
        resolution_status = EmployeeImportDraftStatus.NEW
    elif (
        existing_employee.full_name == full_name
        and existing_employee.position_name == position_name
        and existing_employee.department_name == department_name
        and existing_employee.employment_status == employment_status
    ):
        resolution_status = EmployeeImportDraftStatus.UNCHANGED
    else:
        resolution_status = EmployeeImportDraftStatus.UPDATE

    return EmployeeImportDraft(
        draft_id=None,
        batch_id=batch_id,
        source_row_number=source_row_number,
        personnel_number=personnel_number,
        full_name=full_name,
        position_name=position_name,
        department_name=department_name,
        employment_status=employment_status,
        resolution_status=resolution_status,
        issue_text="; ".join(issue_messages),
    )
