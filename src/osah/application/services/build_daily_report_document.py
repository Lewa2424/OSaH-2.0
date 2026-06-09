from datetime import datetime
from pathlib import Path

from osah.application.services.load_contractor_workspace import load_contractor_workspace
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.domain.entities.daily_report_document import DailyReportDocument
from osah.domain.services.build_daily_report_snapshot import build_daily_report_snapshot
from osah.domain.services.build_daily_report_subject import build_daily_report_subject


# ###### ПОБУДОВА ДОКУМЕНТА ЩОДЕННОГО ЗВІТУ / ПОСТРОЕНИЕ ДОКУМЕНТА ЕЖЕДНЕВНОГО ОТЧЁТА ######
def build_daily_report_document(database_path: Path, created_at: datetime | None = None) -> DailyReportDocument:
    """Повертає згенерований щоденний звіт на основі поточного стану системи.
    Возвращает сгенерированный ежедневный отчёт на основе текущего состояния системы.
    """

    report_created_at = created_at or datetime.now()
    employee_workspace = load_employee_workspace(database_path)
    contractor_workspace = load_contractor_workspace(database_path)
    dashboard_snapshot = load_dashboard_snapshot_from_path(database_path)
    snapshot = build_daily_report_snapshot(
        report_created_at,
        employee_workspace,
        contractor_workspace,
        dashboard_snapshot,
    )
    return DailyReportDocument(
        created_at_text=report_created_at.isoformat(sep=" ", timespec="minutes"),
        subject_text=build_daily_report_subject(report_created_at),
        snapshot=snapshot,
    )
