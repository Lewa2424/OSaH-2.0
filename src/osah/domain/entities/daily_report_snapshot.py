from dataclasses import dataclass

from osah.domain.entities.daily_report_section import DailyReportSection


@dataclass(slots=True)
class DailyReportSnapshot:
    """Структурований знімок даних для щоденного звіту.
    Structured snapshot for rendering the daily report.
    """

    created_at_text: str
    enterprise_name: str
    employee_total: int
    critical_items: int
    warning_items: int
    focus_of_the_day: str
    sections: tuple[DailyReportSection, ...]
    no_remarks_employees: tuple[str, ...]
    no_remarks_contractors: tuple[str, ...]
