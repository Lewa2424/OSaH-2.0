from pathlib import Path

from osah.domain.entities.training_record import TrainingRecord
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_training_records import list_training_records


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ ІНСТРУКТАЖІВ / ЗАГРУЗКА РЕЕСТРА ИНСТРУКТАЖЕЙ ######
def load_training_registry(database_path: Path) -> tuple[TrainingRecord, ...]:
    """Завантажує реєстр інструктажів із локальної бази.
    Загружает реестр инструктажей из локальной базы.
    """

    connection = create_database_connection(database_path)
    try:
        return list_training_records(connection)
    finally:
        connection.close()
