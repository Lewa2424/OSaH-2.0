from dataclasses import dataclass


@dataclass(slots=True)
class DailyReportTableRow:
    """Рядок таблиці щоденного звіту з проблемою.
    A daily report table row describing one problem item.
    """

    subject_block: str
    problem_text: str
    dates_text: str
    notes_text: str
