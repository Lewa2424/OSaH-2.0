import sqlite3
from pathlib import Path


# ###### ВІДНОВЛЕННЯ SQLITE-БАЗИ З РЕЗЕРВНОЇ КОПІЇ / ВОССТАНОВЛЕНИЕ SQLITE-БАЗЫ ИЗ РЕЗЕРВНОЙ КОПИИ ######
def restore_sqlite_backup_file(source_backup_path: Path, target_database_path: Path) -> None:
    """Відновлює локальну SQLite-базу з вибраної резервної копії через API backup.
    Восстанавливает локальную SQLite-базу из выбранной резервной копии через API backup.
    """

    source_connection = sqlite3.connect(source_backup_path)
    target_connection = sqlite3.connect(target_database_path)
    try:
        source_connection.backup(target_connection)
        target_connection.commit()
    finally:
        target_connection.close()
        source_connection.close()
