from pathlib import Path

from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings

AI_DRAWER_TAB_Y_RATIO_KEY = "ai.drawer_tab_y_ratio"
_DEFAULT_TAB_Y_RATIO = 0.5


def load_ai_drawer_tab_y_ratio(database_path: Path) -> float:
    """Читає вертикальну позицію ярлика AI-drawer (0..1).
    Reads the vertical AI drawer tab position as a ratio from 0 to 1.
    """

    connection = create_database_connection(database_path)
    try:
        settings = list_app_settings(connection)
    finally:
        connection.close()

    raw_value = settings.get(AI_DRAWER_TAB_Y_RATIO_KEY, str(_DEFAULT_TAB_Y_RATIO))
    try:
        ratio = float(raw_value)
    except ValueError:
        return _DEFAULT_TAB_Y_RATIO
    return max(0.0, min(1.0, ratio))
