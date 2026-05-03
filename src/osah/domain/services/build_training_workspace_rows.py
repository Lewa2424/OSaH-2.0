from osah.domain.entities.employee import Employee
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.build_training_status_reason import build_training_status_reason
from osah.domain.services.format_training_status_label import format_training_status_label
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ПОБУДОВА РЯДКІВ ІНСТРУКТАЖІВ / BUILD TRAINING ROWS ######
def build_training_workspace_rows(
    employees: tuple[Employee, ...],
    training_records: tuple[TrainingRecord, ...],
) -> tuple[TrainingWorkspaceRow, ...]:
    """Будує рядки реєстру інструктажів із реальних працівників і записів.
    Builds training registry rows from real employees and records.
    """

    employees_by_number = {employee.personnel_number: employee for employee in employees}
    records_by_employee: dict[str, list[TrainingRecord]] = {}
    for record in training_records:
        records_by_employee.setdefault(record.employee_personnel_number, []).append(record)

    rows: list[TrainingWorkspaceRow] = []
    for employee in employees:
        if employee.employment_status.strip().lower() != "active":
            continue
        employee_records = records_by_employee.get(employee.personnel_number, [])
        if not employee_records:
            rows.append(_build_missing_row(employee))
            continue
        for record in sorted(employee_records, key=lambda item: (item.next_control_date or "9999-12-31", item.record_id or 0)):
            rows.append(_build_record_row(record, employees_by_number[record.employee_personnel_number]))
    return tuple(rows)


def _build_missing_row(employee: Employee) -> TrainingWorkspaceRow:
    """Створює рядок відсутнього інструктажу для активного працівника.
    Creates a missing-training row for an active employee.
    """

    return TrainingWorkspaceRow(
        record_id=None,
        employee_personnel_number=employee.personnel_number,
        employee_full_name=employee.full_name,
        department_name=employee.department_name,
        site_name=_infer_site_name(employee.department_name),
        position_name=employee.position_name,
        training_type=None,
        training_type_label="Немає записів",
        event_date="-",
        next_control_date="-",
        status_filter=TrainingRegistryFilter.MISSING,
        status_label=format_training_status_label(TrainingRegistryFilter.MISSING),
        status_reason=build_training_status_reason(TrainingRegistryFilter.MISSING, None, "2099-01-01"),
        conducted_by="-",
        note_text="",
        is_missing=True,
    )


def _build_record_row(record: TrainingRecord, employee: Employee) -> TrainingWorkspaceRow:
    """Створює рядок існуючого запису інструктажу.
    Creates a row for an existing training record.
    """

    status_filter = TrainingRegistryFilter(record.status.value)
    return TrainingWorkspaceRow(
        record_id=record.record_id,
        employee_personnel_number=record.employee_personnel_number,
        employee_full_name=record.employee_full_name,
        department_name=employee.department_name,
        site_name=_infer_site_name(employee.department_name),
        position_name=employee.position_name,
        training_type=record.training_type,
        training_type_label=format_training_type_label(record.training_type),
        event_date=record.event_date,
        next_control_date=record.next_control_date,
        status_filter=status_filter,
        status_label=format_training_status_label(record.status),
        status_reason=build_training_status_reason(record.status, record.training_type, record.next_control_date),
        conducted_by=record.conducted_by,
        note_text=record.note_text,
        is_missing=False,
        work_risk_category=record.work_risk_category,
        next_control_basis=record.next_control_basis,
    )


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
