from osah.domain.entities.employee import Employee
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.build_training_status_reason import build_training_status_reason
from osah.domain.services.format_training_status_label import format_training_status_label
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ПОСТРОЕНИЕ РЯДОВ ИНСТРУКТАЖЕЙ / BUILD TRAINING WORKSPACE ROWS ######
def build_training_workspace_rows(
    employees: tuple[Employee, ...],
    training_records: tuple[TrainingRecord, ...],
) -> tuple[TrainingWorkspaceRow, ...]:
    """Строит строки реестра инструктажей из сотрудников и записей.
    Builds training registry rows from employees and training records.
    """

    employees_by_number = {employee.personnel_number: employee for employee in employees}
    records_by_employee: dict[str, list[TrainingRecord]] = {}
    for record in training_records:
        records_by_employee.setdefault(record.employee_personnel_number, []).append(record)

    rows: list[TrainingWorkspaceRow] = []
    for employee in employees:
        if employee.employment_status.strip().lower() != "active":
            continue
        employee_records = tuple(
            sorted(
                records_by_employee.get(employee.personnel_number, []),
                key=lambda item: (item.next_control_date or "9999-12-31", item.record_id or 0),
            )
        )
        if _should_add_missing_primary_row(employee_records):
            rows.append(_build_missing_primary_row(employee))
        for record in employee_records:
            rows.append(_build_record_row(record, employees_by_number[record.employee_personnel_number]))
    return tuple(rows)


def _should_add_missing_primary_row(employee_records: tuple[TrainingRecord, ...]) -> bool:
    """Определяет, нужно ли показывать отдельную проблему отсутствующего первичного инструктажа.
    Determines whether a dedicated missing-primary row must be shown.
    """

    if not employee_records:
        return True

    latest_introductory = _find_latest_introductory_record(employee_records)
    if latest_introductory is not None:
        return False

    return not any(record.training_type == TrainingType.PRIMARY for record in employee_records)


def _find_latest_introductory_record(employee_records: tuple[TrainingRecord, ...]) -> TrainingRecord | None:
    """Возвращает последний вводный инструктаж сотрудника, если он есть.
    Returns the latest introductory training for the employee when present.
    """

    introductory_records = tuple(
        record for record in employee_records if record.training_type == TrainingType.INTRODUCTORY
    )
    if not introductory_records:
        return None
    return max(introductory_records, key=lambda record: record.event_date)


def _build_missing_primary_row(employee: Employee) -> TrainingWorkspaceRow:
    """Создаёт строку отсутствующего первичного инструктажа для активного сотрудника.
    Creates a missing-primary row for an active employee.
    """

    return TrainingWorkspaceRow(
        record_id=None,
        employee_personnel_number=employee.personnel_number,
        employee_full_name=employee.full_name,
        department_name=employee.department_name,
        site_name=_infer_site_name(employee.department_name),
        position_name=employee.position_name,
        training_type=TrainingType.PRIMARY,
        training_type_label=format_training_type_label(TrainingType.PRIMARY),
        event_date="-",
        next_control_date="-",
        status_filter=TrainingRegistryFilter.MISSING,
        status_label=format_training_status_label(TrainingStatus.MISSING),
        status_reason=build_training_status_reason(TrainingStatus.MISSING, TrainingType.PRIMARY, "-"),
        conducted_by="-",
        note_text="",
        is_missing=True,
    )


def _build_record_row(record: TrainingRecord, employee: Employee) -> TrainingWorkspaceRow:
    """Создаёт строку существующей записи инструктажа.
    Creates a row for an existing training record.
    """

    status_filter = _map_status_to_filter(record.status)
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
        status_reason=build_training_status_reason(
            record.status,
            record.training_type,
            record.next_control_date,
            record.next_control_basis,
        ),
        conducted_by=record.conducted_by,
        note_text=record.note_text,
        is_missing=False,
        person_category=record.person_category,
        requires_primary_on_workplace=record.requires_primary_on_workplace,
        work_risk_category=record.work_risk_category,
        next_control_basis=record.next_control_basis,
    )


def _map_status_to_filter(status: TrainingStatus) -> TrainingRegistryFilter:
    """Сопоставляет доменный статус строки с фильтром реестра.
    Maps a domain record status to a registry filter.
    """

    if status == TrainingStatus.WARNING:
        return TrainingRegistryFilter.WARNING
    if status == TrainingStatus.OVERDUE:
        return TrainingRegistryFilter.OVERDUE
    if status == TrainingStatus.MISSING:
        return TrainingRegistryFilter.MISSING
    return TrainingRegistryFilter.CURRENT


def _infer_site_name(department_name: str) -> str:
    """Выводит участок из названия подразделения для фильтров первой версии.
    Infers a site name from department for first-version filters.
    """

    lowered = department_name.lower()
    if "дільниц" in lowered:
        return department_name
    if "служба" in lowered or "адміністрац" in lowered:
        return "Адміністративний контур"
    return "Основний виробничий контур"
