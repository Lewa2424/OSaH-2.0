from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.domain.services.build_medical_status_reason import build_medical_status_reason
from osah.domain.services.format_medical_decision_label import format_medical_decision_label
from osah.domain.services.format_medical_status_label import format_medical_status_label


# ###### ПОБУДОВА РЯДКІВ МЕДИЦИНИ / BUILD MEDICAL ROWS ######
def build_medical_workspace_rows(
    employees: tuple[Employee, ...],
    medical_records: tuple[MedicalRecord, ...],
) -> tuple[MedicalWorkspaceRow, ...]:
    """Будує рядки реєстру меддопусків із реальних працівників і записів.
    Builds medical registry rows from real employees and records.
    """

    employees_by_number = {employee.personnel_number: employee for employee in employees}
    rows: list[MedicalWorkspaceRow] = []
    for record in medical_records:
        employee = employees_by_number.get(record.employee_personnel_number)
        if employee is None or employee.employment_status.strip().lower() != "active":
            continue
        rows.append(
            MedicalWorkspaceRow(
                record_id=record.record_id,
                employee_personnel_number=record.employee_personnel_number,
                employee_full_name=record.employee_full_name,
                department_name=employee.department_name,
                site_name=_infer_site_name(employee.department_name),
                position_name=employee.position_name,
                valid_from=record.valid_from,
                valid_until=record.valid_until,
                medical_decision=record.medical_decision,
                decision_label=format_medical_decision_label(record.medical_decision),
                restriction_note=record.restriction_note,
                has_restriction=bool(record.restriction_note.strip()),
                status=record.status,
                status_label=format_medical_status_label(record.status),
                status_reason=build_medical_status_reason(record),
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
