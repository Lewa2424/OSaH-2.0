from pathlib import Path

from osah.domain.entities.training_record import TrainingRecord
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.infrastructure.database.queries.list_training_records import list_training_records


# ###### ЗАГРУЗКА РЕЕСТРА ИНСТРУКТАЖЕЙ / LOAD TRAINING REGISTRY ######
def load_training_registry(database_path: Path) -> tuple[TrainingRecord, ...]:
    """Загружает реестр инструктажей из локальной базы с учётом настроек поведения.
    Loads the trainings registry from the local database using behavior settings.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
        warning_days = int(app_settings.get("behavior.training_warning_days", "30") or "30")
        return list_training_records(connection, warning_days=max(1, min(warning_days, 90)))
    finally:
        connection.close()
