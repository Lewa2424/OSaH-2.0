from pathlib import Path

from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ЗБЕРЕЖЕННЯ ПОВЕДІНКОВИХ НАЛАШТУВАНЬ / SAVE BEHAVIOR SETTINGS ######
def save_system_behavior_settings(
    database_path: Path,
    ppe_warning_days: int,
    training_warning_days: int,
    backup_auto_enabled: bool,
    backup_max_copies: int,
) -> None:
    """Persists behavior and backup preferences in app settings."""

    normalized_warning_days = min(max(ppe_warning_days, 1), 90)
    normalized_training_warning_days = min(max(training_warning_days, 1), 90)
    normalized_backup_max_copies = min(max(backup_max_copies, 1), 200)

    connection = create_database_connection(database_path)
    try:
        upsert_app_settings_batch(
            connection,
            {
                "behavior.ppe_warning_days": str(normalized_warning_days),
                "behavior.training_warning_days": str(normalized_training_warning_days),
                "backup.auto_enabled": "1" if backup_auto_enabled else "0",
                "backup.max_copies": str(normalized_backup_max_copies),
            },
        )
        insert_audit_log(
            connection,
            event_type="settings.behavior_updated",
            module_name="settings",
            event_level="info",
            actor_name="inspector",
            entity_name="settings.behavior",
            result_status="success",
            description_text="Behavior and backup preferences updated.",
        )
        connection.commit()
    finally:
        connection.close()
