from datetime import datetime
from pathlib import Path

from osah.application.services.visual.visual_setting_keys import LAST_CRITICAL_SHAKE_AT
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ПОЗНАЧЕННЯ ВИКОНАНОГО CRITICAL-SHAKE / ОТМЕТКА ВЫПОЛНЕННОГО CRITICAL-SHAKE ######
def mark_critical_attention_shake(database_path: Path, current_moment: datetime | None = None) -> None:
    """Зберігає момент останнього виконання короткого critical-shake.
    Сохраняет момент последнего выполнения короткого critical-shake.
    """

    connection = create_database_connection(database_path)
    try:
        upsert_app_setting(
            connection,
            LAST_CRITICAL_SHAKE_AT,
            (current_moment or datetime.now()).isoformat(timespec="seconds"),
        )
        connection.commit()
    finally:
        connection.close()
