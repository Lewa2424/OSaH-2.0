from pathlib import Path

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_registry_row import TrainingRegistryRow
from osah.domain.services.build_training_registry_rows import build_training_registry_rows
from osah.domain.services.filter_training_registry_rows import filter_training_registry_rows
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employees import list_employees
from osah.infrastructure.database.queries.list_training_records import list_training_records


# ###### ЗАВАНТАЖЕННЯ РЯДКІВ РЕЄСТРУ ІНСТРУКТАЖІВ / ЗАГРУЗКА СТРОК РЕЕСТРА ИНСТРУКТАЖЕЙ ######
def load_training_registry_rows(
    database_path: Path,
    registry_filter: TrainingRegistryFilter,
) -> tuple[TrainingRegistryRow, ...]:
    """Повертає відфільтровані рядки реєстру інструктажів із локальної БД.
    Возвращает отфильтрованные строки реестра инструктажей из локальной БД.
    """

    connection = create_database_connection(database_path)
    try:
        rows = build_training_registry_rows(
            list_employees(connection),
            list_training_records(connection),
        )
    finally:
        connection.close()

    return filter_training_registry_rows(rows, registry_filter)
