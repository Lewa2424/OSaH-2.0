from pathlib import Path

from osah.domain.entities.ppe_record import PpeRecord
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_ppe_records import list_ppe_records


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ ЗІЗ / ЗАГРУЗКА РЕЕСТРА СИЗ ######
def load_ppe_registry(database_path: Path) -> tuple[PpeRecord, ...]:
    """Завантажує реєстр ЗІЗ із локальної бази.
    Загружает реестр СИЗ из локальной базы.
    """

    connection = create_database_connection(database_path)
    try:
        return list_ppe_records(connection)
    finally:
        connection.close()
