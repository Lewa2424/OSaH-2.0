from dataclasses import dataclass

from osah.domain.entities.daily_report_snapshot import DailyReportSnapshot


@dataclass(slots=True)
class DailyReportDocument:
    """Згенерований щоденний управлінський звіт.
    Сгенерированный ежедневный управленческий отчёт.
    """

    created_at_text: str
    subject_text: str
    snapshot: DailyReportSnapshot
