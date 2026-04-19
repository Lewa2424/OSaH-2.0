from datetime import datetime
from pathlib import Path

from osah.domain.entities.daily_report_document import DailyReportDocument
from osah.domain.services.build_daily_report_body import build_daily_report_body
from osah.domain.services.build_daily_report_subject import build_daily_report_subject
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path


# ###### ПОБУДОВА ДОКУМЕНТА ЩОДЕННОГО ЗВІТУ / ПОСТРОЕНИЕ ДОКУМЕНТА ЕЖЕДНЕВНОГО ОТЧЁТА ######
def build_daily_report_document(database_path: Path, created_at: datetime | None = None) -> DailyReportDocument:
    """Повертає згенерований щоденний звіт на основі поточного стану системи.
    Возвращает сгенерированный ежедневный отчёт на основе текущего состояния системы.
    """

    report_created_at = created_at or datetime.now()
    dashboard_snapshot = load_dashboard_snapshot_from_path(database_path)
    return DailyReportDocument(
        created_at_text=report_created_at.isoformat(sep=" ", timespec="minutes"),
        subject_text=build_daily_report_subject(report_created_at),
        body_text=build_daily_report_body(report_created_at, dashboard_snapshot),
    )
