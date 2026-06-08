import sqlite3
from pathlib import Path


# ###### СХЕМА РЕЄСТРУ КЛЮЧІВ / KEY REGISTRY SCHEMA ######
def ensure_registry_schema(database_path: Path) -> None:
    """Створює локальну таблицю обліку виданих ключів установки.
    Creates the local registry table for issued setup keys.
    """

    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS key_issue_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                customer TEXT NOT NULL,
                contact TEXT NOT NULL DEFAULT '',
                installation_id TEXT NOT NULL,
                key_kind TEXT NOT NULL,
                previous_record_id INTEGER NULL,
                note TEXT NOT NULL DEFAULT '',
                paste_token TEXT NOT NULL
            );
            """
        )
        connection.commit()
    finally:
        connection.close()
