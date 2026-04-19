import sqlite3
from pathlib import Path


# ###### СТВОРЕННЯ З'ЄДНАННЯ З БД / СОЗДАНИЕ СОЕДИНЕНИЯ С БД ######
def create_database_connection(database_file_path: Path) -> sqlite3.Connection:
    """Створює sqlite-з'єднання з безпечними базовими pragma.
    Создаёт sqlite-соединение с безопасными базовыми pragma.
    """

    connection = sqlite3.connect(database_file_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection
