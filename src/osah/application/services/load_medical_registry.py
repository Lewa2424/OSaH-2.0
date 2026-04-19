from pathlib import Path

from osah.domain.entities.medical_record import MedicalRecord
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_medical_records import list_medical_records


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ МЕДИЦИНИ / ЗАГРУЗКА РЕЕСТРА МЕДИЦИНЫ ######
def load_medical_registry(database_path: Path) -> tuple[MedicalRecord, ...]:
    """Завантажує реєстр медицини з локальної бази.
    Загружает реестр медицины из локальной базы.
    """

    connection = create_database_connection(database_path)
    try:
        return list_medical_records(connection)
    finally:
        connection.close()
