from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.services.build_work_permit_status_reason import build_work_permit_status_reason
from osah.domain.services.format_work_permit_status_label import format_work_permit_status_label


# ###### ПОБУДОВА РЯДКІВ НАРЯДІВ / BUILD WORK PERMIT ROWS ######
def build_work_permit_workspace_rows(
    work_permit_records: tuple[WorkPermitRecord, ...],
    employee_rows: tuple[EmployeeWorkspaceRow, ...],
) -> tuple[WorkPermitWorkspaceRow, ...]:
    """Будує підготовлені рядки нарядів-допусків для Qt без UI-розрахунків.
    Builds prepared work permit rows for Qt without UI calculations.
    """

    employee_lookup = {row.employee.personnel_number: row for row in employee_rows}
    return tuple(_build_row(record, employee_lookup) for record in work_permit_records)


# ###### ПОБУДОВА РЯДКА НАРЯДУ / BUILD WORK PERMIT ROW ######
def _build_row(
    record: WorkPermitRecord,
    employee_lookup: dict[str, EmployeeWorkspaceRow],
) -> WorkPermitWorkspaceRow:
    """Будує один рядок реєстру нарядів-допусків.
    Builds one work permit registry row.
    """

    conflict_reasons = _build_conflict_reasons(record, employee_lookup)
    employee_numbers = tuple(participant.employee_personnel_number for participant in record.participants)
    return WorkPermitWorkspaceRow(
        record=record,
        record_id=record.record_id,
        permit_number=record.permit_number,
        work_kind=record.work_kind,
        work_location=record.work_location,
        department_name=_infer_department_name(record.work_location),
        site_name=record.work_location,
        starts_at=record.starts_at,
        ends_at=record.ends_at,
        responsible_person=record.responsible_person,
        issuer_person=record.issuer_person,
        participant_count=len(record.participants),
        participant_names=", ".join(participant.employee_full_name for participant in record.participants) or "-",
        employee_numbers=employee_numbers,
        status=record.status,
        status_label=format_work_permit_status_label(record.status),
        status_reason=build_work_permit_status_reason(record),
        has_conflicts=bool(conflict_reasons),
        conflict_reasons=conflict_reasons,
    )


# ###### КОНФЛІКТИ ДОПУСКУ / ADMISSION CONFLICTS ######
def _build_conflict_reasons(
    record: WorkPermitRecord,
    employee_lookup: dict[str, EmployeeWorkspaceRow],
) -> tuple[str, ...]:
    """Знаходить блокуючі конфлікти учасників наряду з іншими контурами ОП.
    Finds blocking participant conflicts with other safety modules.
    """

    if record.status in {WorkPermitStatus.CLOSED, WorkPermitStatus.CANCELED}:
        return ()

    reasons: list[str] = []
    for participant in record.participants:
        employee_row = employee_lookup.get(participant.employee_personnel_number)
        if employee_row is None:
            continue
        for problem in employee_row.problems:
            if problem.target_key == "work_permits":
                continue
            if problem.level in {EmployeeStatusLevel.CRITICAL, EmployeeStatusLevel.RESTRICTED}:
                reasons.append(f"{participant.employee_full_name}: {problem.title}")
                break
    return tuple(reasons)


# ###### ВИЗНАЧЕННЯ ПІДРОЗДІЛУ / INFER DEPARTMENT ######
def _infer_department_name(work_location: str) -> str:
    """Виводить підрозділ з місця робіт для першого Qt-релізу.
    Infers a department from work location for the first Qt release.
    """

    if "/" in work_location:
        return work_location.split("/", 1)[0].strip()
    if " - " in work_location:
        return work_location.split(" - ", 1)[0].strip()
    return work_location
