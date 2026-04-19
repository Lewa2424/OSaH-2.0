import sqlite3
from pathlib import Path


# ###### СТВОРЕННЯ SQLITE-РЕЗЕРВНОЇ КОПІЇ / СОЗДАНИЕ SQLITE-РЕЗЕРВНОЙ КОПИИ ######
def create_sqlite_backup_file(source_database_path: Path, target_backup_path: Path) -> None:
    """Створює узгоджену резервну копію SQLite-бази через вбудований API backup.
    Создаёт согласованную резервную копию SQLite-базы через встроенный API backup.
    """

    target_backup_path.parent.mkdir(parents=True, exist_ok=True)
    source_connection = sqlite3.connect(source_database_path)
    target_connection = sqlite3.connect(target_backup_path)
    try:
        source_connection.backup(target_connection)
        target_connection.commit()
    finally:
        target_connection.close()
        source_connection.close()
