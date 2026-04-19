from pathlib import Path

from osah.domain.entities.employee import Employee
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employees import list_employees


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ ПРАЦІВНИКІВ / ЗАГРУЗКА РЕЕСТРА СОТРУДНИКОВ ######
def load_employee_registry(database_path: Path) -> tuple[Employee, ...]:
    """Завантажує реєстр працівників із локальної бази даних.
    Загружает реестр сотрудников из локальной базы данных.
    """

    connection = create_database_connection(database_path)
    try:
        return list_employees(connection)
    finally:
        connection.close()
