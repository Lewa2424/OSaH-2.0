from osah.domain.entities.employee_problem import EmployeeProblem
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### СТРОКИ ТА ДАТИ ДЛЯ ПРОБЛЕМИ ЗВІТУ / BUILD DAILY REPORT DATES FOR PROBLEM ######
def build_daily_report_dates_for_problem(
    row: EmployeeWorkspaceRow,
    problem: EmployeeProblem,
) -> tuple[str, str]:
    """Повертає текст строків/дат і приміток для проблеми працівника у звіті.
    Returns dates/deadlines text and notes for an employee problem in the report.
    """

    target_key = problem.target_key
    if target_key == "trainings":
        return _build_training_dates_notes(row)
    if target_key == "ppe":
        return _build_ppe_dates_notes(row)
    if target_key == "medical":
        return _build_medical_dates_notes(row)
    if target_key == "work_permits":
        return _build_work_permit_dates_notes(row)
    return "—", problem.detail


def _build_training_dates_notes(row: EmployeeWorkspaceRow) -> tuple[str, str]:
    if not row.training_records:
        return "Контроль: відсутній запис", ""
    record = row.training_records[0]
    lines = [f"Подія: {record.event_date}"]
    if record.next_control_date.strip():
        lines.append(f"Наступний контроль: {record.next_control_date}")
    note_parts = [part for part in (record.knowledge_check_note, record.note_text) if part.strip()]
    return "\n".join(lines), "\n".join(note_parts)


def _build_ppe_dates_notes(row: EmployeeWorkspaceRow) -> tuple[str, str]:
    if not row.ppe_records:
        return "Записи ЗІЗ: відсутні", ""
    problem_records = tuple(
        record
        for record in row.ppe_records
        if record.status in {PpeStatus.EXPIRED, PpeStatus.NOT_ISSUED, PpeStatus.WARNING}
    ) or row.ppe_records[:1]
    lines: list[str] = []
    notes: list[str] = []
    for record in problem_records[:3]:
        lines.append(f"{record.ppe_name}: видача {record.issue_date}, заміна {record.replacement_date}")
        if record.note_text.strip():
            notes.append(record.note_text.strip())
    return "\n".join(lines), "\n".join(notes)


def _build_medical_dates_notes(row: EmployeeWorkspaceRow) -> tuple[str, str]:
    if not row.medical_records:
        return "Меддопуск: відсутній", ""
    record = row.medical_records[0]
    lines = [f"Дійсний: {record.valid_from} — {record.valid_until}"]
    notes: list[str] = []
    if record.restriction_note.strip():
        notes.append(record.restriction_note.strip())
    if record.status == MedicalStatus.RESTRICTED:
        notes.append("Є обмеження за меддопуском.")
    if record.basis_note.strip():
        notes.append(record.basis_note.strip())
    return "\n".join(lines), "\n".join(notes)


def _build_work_permit_dates_notes(row: EmployeeWorkspaceRow) -> tuple[str, str]:
    active_records = tuple(
        record
        for record in row.work_permit_records
        if record.status not in {WorkPermitStatus.CLOSED, WorkPermitStatus.CANCELED, WorkPermitStatus.REISSUED}
    )
    if not active_records:
        return "Активні наряди: немає", ""
    lines: list[str] = []
    notes: list[str] = []
    for record in active_records[:2]:
        lines.append(f"{record.permit_number}: {record.starts_at} — {record.ends_at}")
        if record.note_text.strip():
            notes.append(record.note_text.strip())
    return "\n".join(lines), "\n".join(notes)
