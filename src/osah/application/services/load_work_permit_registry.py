from pathlib import Path

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_work_permit_records import list_work_permit_records


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ НАРЯДІВ-ДОПУСКІВ / ЗАГРУЗКА РЕЕСТРА НАРЯДОВ-ДОПУСКОВ ######
def load_work_permit_registry(database_path: Path) -> tuple[WorkPermitRecord, ...]:
    """Завантажує реєстр нарядів-допусків з локальної бази.
    Загружает реестр нарядов-допусков из локальной базы.
    """

    connection = create_database_connection(database_path)
    try:
        return list_work_permit_records(connection)
    finally:
        connection.close()
