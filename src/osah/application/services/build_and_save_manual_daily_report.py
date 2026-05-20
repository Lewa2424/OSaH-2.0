from datetime import datetime
from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.load_manual_report_settings import load_manual_report_settings
from osah.application.services.save_daily_report_copy import save_daily_report_copy
from osah.application.services.save_manual_report_settings import save_manual_report_settings
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.manual_report_settings import ManualReportSettings
from osah.domain.entities.manual_report_save_result import ManualReportSaveResult
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### РУЧНЕ ФОРМУВАННЯ ТА ЗБЕРЕЖЕННЯ ЩОДЕННОГО ЗВІТУ / BUILD AND SAVE MANUAL DAILY REPORT ######
def build_and_save_manual_daily_report(
    database_path: Path,
    target_path: Path,
    *,
    access_role: AccessRole,
) -> ManualReportSaveResult:
    """Формує щоденний звіт, зберігає його у вибраний шлях та внутрішню історію.
    Builds the daily report, saves it to the chosen path and to the internal history.
    """

    ensure_write_access(access_role, "build_and_save_manual_daily_report")
    report_document = build_daily_report_document(database_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = f"{report_document.subject_text}\n\n{report_document.body_text}"
    target_path.write_text(report_text, encoding="utf-8")
    internal_copy_path = save_daily_report_copy(database_path, report_document)

    current_settings = load_manual_report_settings(database_path)
    updated_settings = ManualReportSettings(
        manual_reminder_enabled=current_settings.manual_reminder_enabled,
        manual_reminder_time=current_settings.manual_reminder_time,
        last_generated_date=datetime.now().strftime("%Y-%m-%d"),
        last_skipped_date="",
        next_prompt_at="",
        default_save_directory=current_settings.default_save_directory,
        ask_save_path_each_time=current_settings.ask_save_path_each_time,
    )
    save_manual_report_settings(database_path, updated_settings, access_role=access_role)

    connection = create_database_connection(database_path)
    try:
        insert_audit_log(
            connection,
            event_type="report.file_created",
            module_name="reports",
            event_level="info",
            actor_name="user",
            entity_name="daily_report",
            result_status="success",
            description_text=f"saved_path={target_path};internal_copy={internal_copy_path}",
        )
        connection.commit()
    finally:
        connection.close()

    return ManualReportSaveResult(
        user_file_path=target_path,
        internal_copy_path=internal_copy_path,
        created_at_text=report_document.created_at_text,
    )
