from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.manual_report_settings import ManualReportSettings
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ЗБЕРЕЖЕННЯ НАЛАШТУВАНЬ РУЧНОГО ЗВІТУ / SAVE MANUAL REPORT SETTINGS ######
def save_manual_report_settings(
    database_path: Path,
    manual_report_settings: ManualReportSettings,
    *,
    access_role: AccessRole,
) -> None:
    """Зберігає налаштування нагадування та ручного формування щоденного звіту.
    Saves reminder settings and manual daily report workflow state.
    """

    ensure_write_access(access_role, "save_manual_report_settings")
    connection = create_database_connection(database_path)
    try:
        setting_pairs = {
            "report.manual_reminder_enabled": "1" if manual_report_settings.manual_reminder_enabled else "0",
            "report.manual_reminder_time": manual_report_settings.manual_reminder_time.strip() or "08:00",
            "report.last_generated_date": manual_report_settings.last_generated_date.strip(),
            "report.last_skipped_date": manual_report_settings.last_skipped_date.strip(),
            "report.next_prompt_at": manual_report_settings.next_prompt_at.strip(),
            "report.default_save_directory": manual_report_settings.default_save_directory.strip(),
            "report.ask_save_path_each_time": "1" if manual_report_settings.ask_save_path_each_time else "0",
            "report.last_saved_file_path": manual_report_settings.last_saved_file_path.strip(),
        }
        for setting_key, setting_value in setting_pairs.items():
            upsert_app_setting(connection, setting_key, setting_value)
        insert_audit_log(
            connection,
            event_type="report.settings_updated",
            module_name="reports",
            event_level="info",
            actor_name="system",
            entity_name="report.settings",
            result_status="success",
            description_text="Manual report settings updated.",
        )
        connection.commit()
    finally:
        connection.close()
