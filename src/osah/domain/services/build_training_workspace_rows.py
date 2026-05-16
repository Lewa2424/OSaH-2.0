from osah.domain.entities.employee import Employee
from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.services.build_training_status_reason import build_training_status_reason
from osah.domain.services.find_training_chronology_conflict_reason import find_training_chronology_conflict_reason
from osah.domain.services.format_training_status_label import format_training_status_label
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ПОСТРОЕНИЕ РЯДОВ ИНСТРУКТАЖЕЙ / BUILD TRAINING WORKSPACE ROWS ######
def build_training_workspace_rows(
    employees: tuple[Employee, ...],
    training_records: tuple[TrainingRecord, ...],
) -> tuple[TrainingWorkspaceRow, ...]:
    """Строит строки реестра инструктажей из сотрудников и записей.
    Builds training registry rows from employees and records.
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
            rows.append(
                _build_record_row(
                    record,
                    employees_by_number[record.employee_personnel_number],
                    employee_records,
                )
            )
    return tuple(rows)


def _should_add_missing_primary_row(employee_records: tuple[TrainingRecord, ...]) -> bool:
    if not employee_records:
        return True

    latest_introductory = _find_latest_introductory_record(employee_records)
    if latest_introductory is not None:
        if latest_introductory.next_control_basis == TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY:
            return False
        if latest_introductory.next_control_basis == TrainingNextControlBasis.INTRODUCTORY_PRIMARY_NOT_REQUIRED:
            return False

    return not any(record.training_type == TrainingType.PRIMARY for record in employee_records)


def _find_latest_introductory_record(employee_records: tuple[TrainingRecord, ...]) -> TrainingRecord | None:
    introductory_records = tuple(
        record for record in employee_records if record.training_type == TrainingType.INTRODUCTORY
    )
    if not introductory_records:
        return None
    return max(introductory_records, key=lambda record: record.event_date)


def _build_missing_primary_row(employee: Employee) -> TrainingWorkspaceRow:
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
        next_control_date="Потрібен",
        status_filter=TrainingRegistryFilter.MISSING,
        status_label=format_training_status_label(TrainingStatus.MISSING),
        status_reason="Не зафіксовано первинний інструктаж.\nПотрібно внести запис для допуску до роботи.",
        conducted_by="-",
        note_text="",
        is_missing=True,
    )


def _build_record_row(
    record: TrainingRecord,
    employee: Employee,
    employee_records: tuple[TrainingRecord, ...],
) -> TrainingWorkspaceRow:
    next_control_date = record.next_control_date
    status_filter = _map_status_to_filter(record.status)
    status_label = format_training_status_label(record.status)
    status_reason = build_training_status_reason(
        record.status,
        record.training_type,
        record.next_control_date,
        record.next_control_basis,
    )
    chronology_conflict_reason = find_training_chronology_conflict_reason(record, employee_records)
    if chronology_conflict_reason is not None:
        status_filter = TrainingRegistryFilter.INVALID
        status_label = format_training_status_label(TrainingStatus.INVALID)
        status_reason = chronology_conflict_reason

    if record.training_type == TrainingType.INTRODUCTORY:
        primary_record = _find_closing_primary_record(employee_records, record)
        if primary_record is not None:
            next_control_date = "-"
            status_filter = TrainingRegistryFilter.CURRENT
            status_label = "Закрито"
            status_reason = (
                "Первинний інструктаж на робочому місці зафіксовано.\n"
                f"Цей вступний запис закрито записом від {primary_record.event_date}."
            )
        elif record.next_control_basis == TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY:
            next_control_date = "Потрібен"
            status_reason = (
                "Після вступного потрібен первинний інструктаж\n"
                "до допуску до самостійної роботи."
            )
        else:
            next_control_date = "-"

    elif chronology_conflict_reason is None and record.training_type == TrainingType.PRIMARY:
        if _find_required_introductory_record(employee_records, record) is None:
            next_control_date = "Потрібен"
            status_filter = TrainingRegistryFilter.MISSING
            status_label = "Відсутній"
            status_reason = (
                "Не зафіксовано вступний інструктаж,\n"
                "який має передувати первинному."
            )
        else:
            later_cycle_record = _find_later_repeated_cycle_record(employee_records, record)
            if later_cycle_record is not None:
                next_control_date = "-"
                status_filter = TrainingRegistryFilter.CURRENT
                status_label = "Закрито"
                status_reason = (
                    "Цю контрольну точку закрито новішим записом:\n"
                    f"{format_training_type_label(later_cycle_record.training_type)} від {later_cycle_record.event_date}."
                )

    elif chronology_conflict_reason is None and record.training_type in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}:
        if not record.next_control_date.strip():
            next_control_date = "-"

    elif chronology_conflict_reason is None and record.training_type == TrainingType.REPEATED:
        later_cycle_record = _find_later_repeated_cycle_record(employee_records, record)
        if later_cycle_record is not None:
            next_control_date = "-"
            status_filter = TrainingRegistryFilter.CURRENT
            status_label = "Закрито"
            status_reason = (
                "Цю контрольну точку закрито новішим записом:\n"
                f"{format_training_type_label(later_cycle_record.training_type)} від {later_cycle_record.event_date}."
            )

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
        next_control_date=next_control_date,
        status_filter=status_filter,
        status_label=status_label,
        status_reason=status_reason,
        conducted_by=record.conducted_by,
        note_text=record.note_text,
        is_missing=False,
        person_category=record.person_category,
        requires_primary_on_workplace=record.requires_primary_on_workplace,
        work_risk_category=record.work_risk_category,
        next_control_basis=record.next_control_basis,
        knowledge_check_result=record.knowledge_check_result,
        work_admission_status=record.work_admission_status,
        knowledge_check_note=record.knowledge_check_note,
        basis_text=record.basis_text,
        basis_note=record.basis_note,
    )


def _find_closing_primary_record(
    employee_records: tuple[TrainingRecord, ...],
    introductory_record: TrainingRecord,
) -> TrainingRecord | None:
    primary_records = tuple(
        record
        for record in employee_records
        if record.training_type == TrainingType.PRIMARY
        and record.event_date >= introductory_record.event_date
    )
    if not primary_records:
        return None
    return min(primary_records, key=lambda record: (record.event_date, record.record_id or 0))


def _find_required_introductory_record(
    employee_records: tuple[TrainingRecord, ...],
    primary_record: TrainingRecord,
) -> TrainingRecord | None:
    introductory_records = tuple(
        record
        for record in employee_records
        if record.training_type == TrainingType.INTRODUCTORY
        and record.event_date <= primary_record.event_date
    )
    if not introductory_records:
        return None
    return max(introductory_records, key=lambda record: (record.event_date, record.record_id or 0))


def _find_later_repeated_cycle_record(
    employee_records: tuple[TrainingRecord, ...],
    training_record: TrainingRecord,
) -> TrainingRecord | None:
    later_records = tuple(
        record
        for record in employee_records
        if _is_repeated_cycle_record(record)
        and (record.event_date, record.record_id or 0) > (training_record.event_date, training_record.record_id or 0)
    )
    if not later_records:
        return None
    return min(later_records, key=lambda record: (record.event_date, record.record_id or 0))


def _is_repeated_cycle_record(training_record: TrainingRecord) -> bool:
    if training_record.training_type in {TrainingType.PRIMARY, TrainingType.REPEATED}:
        return True
    if training_record.training_type not in {TrainingType.UNSCHEDULED, TrainingType.TARGETED}:
        return False
    return bool(training_record.next_control_date.strip())


def _map_status_to_filter(status: TrainingStatus) -> TrainingRegistryFilter:
    if status == TrainingStatus.INVALID:
        return TrainingRegistryFilter.INVALID
    if status == TrainingStatus.WARNING:
        return TrainingRegistryFilter.WARNING
    if status == TrainingStatus.OVERDUE:
        return TrainingRegistryFilter.OVERDUE
    if status == TrainingStatus.MISSING:
        return TrainingRegistryFilter.MISSING
    return TrainingRegistryFilter.CURRENT


def _infer_site_name(department_name: str) -> str:
    lowered = department_name.lower()
    if "дільниц" in lowered:
        return department_name
    if "служба" in lowered or "адмініст" in lowered:
        return "Адміністративний контур"
    return "Основний виробничий контур"
