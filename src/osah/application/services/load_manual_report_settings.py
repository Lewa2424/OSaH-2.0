from pathlib import Path

from osah.domain.entities.manual_report_settings import ManualReportSettings
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


# ###### ЗАВАНТАЖЕННЯ НАЛАШТУВАНЬ РУЧНОГО ЗВІТУ / LOAD MANUAL REPORT SETTINGS ######
def load_manual_report_settings(database_path: Path) -> ManualReportSettings:
    """Повертає збережені налаштування ручного сценарію щоденного звіту.
    Returns saved settings for the manual daily report workflow.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    return ManualReportSettings(
        manual_reminder_enabled=app_settings.get("report.manual_reminder_enabled", "0") == "1",
        manual_reminder_time=app_settings.get("report.manual_reminder_time", "08:00") or "08:00",
        last_generated_date=app_settings.get("report.last_generated_date", ""),
        last_skipped_date=app_settings.get("report.last_skipped_date", ""),
        next_prompt_at=app_settings.get("report.next_prompt_at", ""),
        default_save_directory=app_settings.get("report.default_save_directory", ""),
        ask_save_path_each_time=app_settings.get("report.ask_save_path_each_time", "1") == "1",
    )
