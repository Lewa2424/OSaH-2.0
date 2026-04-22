from osah.domain.entities.employee import Employee
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.services.build_ppe_status_reason import build_ppe_status_reason
from osah.domain.services.format_ppe_status_label import format_ppe_status_label


# ###### ПОБУДОВА РЯДКІВ ЗІЗ / BUILD PPE ROWS ######
def build_ppe_workspace_rows(
    employees: tuple[Employee, ...],
    ppe_records: tuple[PpeRecord, ...],
) -> tuple[PpeWorkspaceRow, ...]:
    """Будує рядки реєстру ЗІЗ із реальних працівників і записів.
    Builds PPE registry rows from real employees and records.
    """

    employees_by_number = {employee.personnel_number: employee for employee in employees}
    rows: list[PpeWorkspaceRow] = []
    for record in ppe_records:
        employee = employees_by_number.get(record.employee_personnel_number)
        if employee is None or employee.employment_status.strip().lower() != "active":
            continue
        rows.append(
            PpeWorkspaceRow(
                record_id=record.record_id,
                employee_personnel_number=record.employee_personnel_number,
                employee_full_name=record.employee_full_name,
                department_name=employee.department_name,
                site_name=_infer_site_name(employee.department_name),
                position_name=employee.position_name,
                ppe_name=record.ppe_name,
                is_required=record.is_required,
                is_issued=record.is_issued,
                issue_date=record.issue_date,
                replacement_date=record.replacement_date,
                quantity=record.quantity,
                status=record.status,
                status_label=format_ppe_status_label(record.status),
                status_reason=build_ppe_status_reason(record),
                note_text=record.note_text,
            )
        )
    return tuple(rows)


def _infer_site_name(department_name: str) -> str:
    """Виводить участок із назви підрозділу для фільтрів першої версії.
    Infers a site name from department for first-version filters.
    """

    lowered = department_name.lower()
    if "дільниц" in lowered:
        return department_name
    if "служба" in lowered or "адміністрац" in lowered:
        return "Адміністративний контур"
    return "Основний виробничий контур"
