from datetime import datetime
from pathlib import Path

from osah.domain.entities.backup_kind import BackupKind
from osah.infrastructure.backups.build_backup_directory_path import build_backup_directory_path
from osah.infrastructure.backups.build_backup_file_name import build_backup_file_name
from osah.infrastructure.backups.create_sqlite_backup_file import create_sqlite_backup_file
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.logging.log_system_event import log_system_event


# ###### СТВОРЕННЯ РЕЗЕРВНОЇ КОПІЇ / СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ ######
def create_backup_snapshot(database_path: Path, backup_kind: BackupKind) -> Path:
    """Створює резервну копію локальної БД вказаного типу й повертає шлях до файлу.
    Создаёт резервную копию локальной БД указанного типа и возвращает путь к файлу.
    """

    created_at = datetime.now()
    backup_directory_path = build_backup_directory_path(database_path)
    backup_file_path = backup_directory_path / build_backup_file_name(backup_kind, created_at)
    create_sqlite_backup_file(database_path, backup_file_path)
    log_system_event("backup_restore", f"Backup snapshot created: kind={backup_kind.value};file={backup_file_path.name}")

    connection = create_database_connection(database_path)
    try:
        insert_audit_log(
            connection,
            event_type=f"backup.{backup_kind.value}",
            module_name="backup_restore",
            event_level="info",
            actor_name="system",
            entity_name=backup_file_path.name,
            result_status="success",
            description_text=f"path={backup_file_path}",
        )
        connection.commit()
    finally:
        connection.close()
    return backup_file_path
