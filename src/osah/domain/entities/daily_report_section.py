from dataclasses import dataclass

from osah.domain.entities.daily_report_table_row import DailyReportTableRow


@dataclass(slots=True)
class DailyReportSection:
    """Секція щоденного звіту з таблицею проблем.
    A daily report section with a problem table.
    """

    title: str
    rows: tuple[DailyReportTableRow, ...]
