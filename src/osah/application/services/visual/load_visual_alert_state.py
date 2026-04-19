from pathlib import Path

from osah.application.services.visual.should_trigger_critical_attention_shake import (
    should_trigger_critical_attention_shake,
)
from osah.application.services.visual.visual_setting_keys import LAST_CRITICAL_SHAKE_AT
from osah.domain.entities.visual_alert_state import VisualAlertState
from osah.domain.services.build_section_alert_levels import build_section_alert_levels
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.infrastructure.database.queries.list_notifications import list_notifications


# ###### ЗАВАНТАЖЕННЯ СТАНУ ВІЗУАЛЬНИХ ТРИВОГ / ЗАГРУЗКА СОСТОЯНИЯ ВИЗУАЛЬНЫХ ТРЕВОГ ######
def load_visual_alert_state(database_path: Path) -> VisualAlertState:
    """Зчитує рівні тривоги розділів і потребу в короткому critical-shake.
    Считывает уровни тревоги разделов и потребность в коротком critical-shake.
    """

    connection = create_database_connection(database_path)
    try:
        notifications = list_notifications(connection)
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    section_levels = build_section_alert_levels(notifications)
    return VisualAlertState(
        section_levels=section_levels,
        should_shake=should_trigger_critical_attention_shake(
            section_levels,
            app_settings.get(LAST_CRITICAL_SHAKE_AT, ""),
        ),
    )
