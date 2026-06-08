from pathlib import Path

from osah.infrastructure.config.is_demo_timed_distribution_enabled import (
    is_demo_timed_distribution_enabled_in_settings,
    is_demo_timed_distribution_marker_present,
)
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


# ###### АКТИВНІСТЬ DEMO-ДИСТРИБУЦІЇ / DEMO DISTRIBUTION ACTIVE CHECK ######
def is_demo_timed_distribution_active(database_path: Path) -> bool:
    """Повертає True для demo-only установки: маркер або прапорець у базі.
    Returns True for demo-only installs via marker file or persisted DB flag.
    """

    if is_demo_timed_distribution_marker_present(database_path.parent.parent):
        return True

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()
    return is_demo_timed_distribution_enabled_in_settings(app_settings)
