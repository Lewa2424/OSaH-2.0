from pathlib import Path

from osah.application.services.ai.load_ai_drawer_tab_y_ratio import AI_DRAWER_TAB_Y_RATIO_KEY
from osah.domain.entities.access_role import AccessRole
from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection


def save_ai_drawer_tab_y_ratio(
    database_path: Path,
    *,
    tab_y_ratio: float,
    access_role: AccessRole,
) -> None:
    """Зберігає вертикальну позицію ярлика AI-drawer (0..1).
    Saves the vertical AI drawer tab position as a ratio from 0 to 1.
    """

    ensure_write_access(access_role, "save_ai_drawer_tab_y_ratio")
    clamped_ratio = max(0.0, min(1.0, tab_y_ratio))
    connection = create_database_connection(database_path)
    try:
        upsert_app_setting(
            connection,
            AI_DRAWER_TAB_Y_RATIO_KEY,
            f"{clamped_ratio:.4f}",
        )
        connection.commit()
    finally:
        connection.close()
