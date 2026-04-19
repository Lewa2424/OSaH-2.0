from pathlib import Path

from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.application.services.load_dashboard_snapshot import load_dashboard_snapshot


# ###### ЗАВАНТАЖЕННЯ ЗНІМКУ ГОЛОВНОГО ЕКРАНА З БАЗИ / ЗАГРУЗКА СНИМКА ГЛАВНОГО ЭКРАНА ИЗ БАЗЫ ######
def load_dashboard_snapshot_from_path(database_path: Path) -> DashboardSnapshot:
    """Повертає актуальний знімок головного екрана з локальної бази.
    Возвращает актуальный снимок главного экрана из локальной базы.
    """

    connection = create_database_connection(database_path)
    try:
        return load_dashboard_snapshot(connection)
    finally:
        connection.close()
