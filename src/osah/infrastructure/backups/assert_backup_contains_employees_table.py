import sqlite3
from pathlib import Path


# ###### ПЕРЕВІРКА ТАБЛИЦІ EMPLOYEES У БЕКАПІ / ASSERT EMPLOYEES TABLE IN BACKUP ######
def assert_backup_contains_employees_table(backup_file_path: Path) -> None:
    """Перевіряє, що файл резервної копії містить таблицю employees.
    Verifies that the backup file contains an employees table.
    """

    connection = sqlite3.connect(f"file:{backup_file_path}?mode=ro", uri=True)
    try:
        table_row = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'employees' LIMIT 1"
        ).fetchone()
        if table_row is None:
            raise ValueError("Резервна копія не містить таблицю employees і не підходить для ClearWork.")
    finally:
        connection.close()
