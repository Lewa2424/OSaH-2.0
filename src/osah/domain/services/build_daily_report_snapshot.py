from datetime import datetime

from osah.domain.entities.contractor_readiness_status import ContractorReadinessStatus
from osah.domain.entities.contractor_workspace import ContractorWorkspace
from osah.domain.entities.daily_report_section import DailyReportSection
from osah.domain.entities.daily_report_snapshot import DailyReportSnapshot
from osah.domain.entities.daily_report_table_row import DailyReportTableRow
from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.domain.services.build_contractor_readiness_snapshot import build_contractor_readiness_snapshot
from osah.domain.services.build_daily_report_dates_for_problem import build_daily_report_dates_for_problem
from osah.domain.services.build_daily_report_employee_block import build_daily_report_employee_block

_EMPLOYEE_SECTIONS: tuple[tuple[str, str], ...] = (
    ("Інструктажі", "Інструктажі"),
    ("ЗІЗ", "ЗІЗ"),
    ("Медицина", "Медицина"),
    ("Наряди-допуски", "Наряди-допуски"),
)


# ###### ПОБУДОВА ЗНІМКА ЩОДЕННОГО ЗВІТУ / BUILD DAILY REPORT SNAPSHOT ######
def build_daily_report_snapshot(
    created_at: datetime,
    employee_workspace: EmployeeWorkspace,
    contractor_workspace: ContractorWorkspace,
    dashboard_snapshot: DashboardSnapshot,
) -> DailyReportSnapshot:
    """Збирає структурований знімок щоденного звіту з робочих просторів.
    Builds a structured daily report snapshot from workspace data.
    """

    employee_sections = tuple(
        DailyReportSection(
            title=section_title,
            rows=_build_employee_section_rows(employee_workspace, module_name),
        )
        for section_title, module_name in _EMPLOYEE_SECTIONS
    )
    contractor_section = DailyReportSection(
        title="Підрядники",
        rows=_build_contractor_section_rows(contractor_workspace),
    )
    no_remarks_employees = tuple(
        f"таб. № {row.employee.personnel_number} — {row.employee.full_name}"
        for row in employee_workspace.rows
        if not row.problems and row.status_level == EmployeeStatusLevel.NORMAL
    )
    no_remarks_contractors = tuple(
        f"{record.company_name}"
        for record in contractor_workspace.records
        if record.activity_status == "active"
        and build_contractor_readiness_snapshot(record).status == ContractorReadinessStatus.READY
    )

    return DailyReportSnapshot(
        created_at_text=created_at.strftime("%Y-%m-%d %H:%M"),
        enterprise_name=employee_workspace.enterprise_name,
        employee_total=dashboard_snapshot.employee_total,
        critical_items=dashboard_snapshot.critical_items,
        warning_items=dashboard_snapshot.warning_items,
        focus_of_the_day=dashboard_snapshot.focus_of_the_day,
        sections=employee_sections + (contractor_section,),
        no_remarks_employees=no_remarks_employees,
        no_remarks_contractors=no_remarks_contractors,
    )


def _build_employee_section_rows(
    employee_workspace: EmployeeWorkspace,
    module_name: str,
) -> tuple[DailyReportTableRow, ...]:
    rows: list[DailyReportTableRow] = []
    for workspace_row in employee_workspace.rows:
        module_problems = tuple(
            problem for problem in workspace_row.problems if problem.module_name == module_name
        )
        for problem in module_problems:
            dates_text, notes_text = build_daily_report_dates_for_problem(workspace_row, problem)
            rows.append(
                DailyReportTableRow(
                    subject_block=build_daily_report_employee_block(workspace_row),
                    problem_text=f"{problem.title}. {problem.detail}".strip(),
                    dates_text=dates_text or "—",
                    notes_text=notes_text or "—",
                )
            )
    return tuple(rows)


def _build_contractor_section_rows(
    contractor_workspace: ContractorWorkspace,
) -> tuple[DailyReportTableRow, ...]:
    rows: list[DailyReportTableRow] = []
    for record in contractor_workspace.records:
        if record.activity_status != "active":
            continue
        readiness = build_contractor_readiness_snapshot(record)
        if readiness.status == ContractorReadinessStatus.READY:
            continue
        subject_block = record.company_name
        if record.contact_person.strip():
            subject_block = f"{record.company_name}\n{record.contact_person}"
        if record.contact_phone.strip():
            subject_block = f"{subject_block}\n{record.contact_phone}"
        dates_text = record.work_scope_text.strip() or "—"
        notes_parts = [part for part in (record.note_text, record.enterprise_supervisor) if part.strip()]
        rows.append(
            DailyReportTableRow(
                subject_block=subject_block,
                problem_text=f"{readiness.headline_text}. {readiness.issues_text}".strip(),
                dates_text=dates_text,
                notes_text="\n".join(notes_parts) if notes_parts else "—",
            )
        )
    return tuple(rows)
