from pathlib import Path

from osah.application.services.create_backup_snapshot import create_backup_snapshot
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.backup_kind import BackupKind
from osah.infrastructure.backups.restore_sqlite_backup_file import restore_sqlite_backup_file
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.schema.ensure_core_schema import ensure_core_schema
from osah.infrastructure.logging.log_alert_event import log_alert_event
from osah.infrastructure.logging.log_system_event import log_system_event


# ###### ВІДНОВЛЕННЯ З РЕЗЕРВНОЇ КОПІЇ / ВОССТАНОВЛЕНИЕ ИЗ РЕЗЕРВНОЙ КОПИИ ######
def restore_backup_snapshot(database_path: Path, backup_file_path: Path) -> Path:
    """Відновлює локальну БД з обраної резервної копії та повертає шлях до страховочної копії.
    Восстанавливает локальную БД из выбранной резервной копии и возвращает путь к страховочной копии.
    """

    if not backup_file_path.exists():
        log_alert_event("backup_restore", f"Restore failed because backup file was not found: {backup_file_path}")
        raise ValueError("Обрану резервну копію не знайдено.")

    safety_backup_path = create_backup_snapshot(database_path, BackupKind.SAFETY)
    restore_sqlite_backup_file(backup_file_path, database_path)

    connection = create_database_connection(database_path)
    try:
        ensure_core_schema(connection)
        sync_control_notifications(connection)
        insert_audit_log(
            connection,
            event_type="restore.completed",
            module_name="backup_restore",
            event_level="warning",
            actor_name="system",
            entity_name=backup_file_path.name,
            result_status="success",
            description_text=f"safety_copy={safety_backup_path.name}",
        )
        connection.commit()
    finally:
        connection.close()

    log_system_event(
        "backup_restore",
        f"Restore completed successfully: restored_from={backup_file_path.name};safety_copy={safety_backup_path.name}",
    )
    return safety_backup_path
