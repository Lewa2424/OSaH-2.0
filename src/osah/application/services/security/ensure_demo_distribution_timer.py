from datetime import datetime, timedelta
from pathlib import Path
from sqlite3 import Connection

from osah.application.services.security.security_setting_keys import (
    DEMO_DISTRIBUTION_ENABLED,
    DEMO_EXPIRES_AT,
    DEMO_STARTED_AT,
)
from osah.domain.services.demo_distribution_duration_hours import DEMO_DISTRIBUTION_DURATION_HOURS
from osah.infrastructure.config.is_demo_timed_distribution_enabled import (
    is_demo_timed_distribution_enabled_in_settings,
    is_demo_timed_distribution_marker_present,
)
from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


# ###### ІНІЦІАЛІЗАЦІЯ ТАЙМЕРА DEMO-ДИСТРИБУЦІЇ / ENSURE DEMO DISTRIBUTION TIMER ######
def ensure_demo_distribution_timer(connection: Connection, project_root: Path) -> None:
    """Запускає 48-годинний таймер demo-only установки при першому запуску.
    Starts the 48-hour demo-only timer on the first application bootstrap.
    """

    if not is_demo_timed_distribution_marker_present(project_root):
        app_settings = list_app_settings(connection)
        if not is_demo_timed_distribution_enabled_in_settings(app_settings):
            return

    app_settings = list_app_settings(connection)
    if app_settings.get(DEMO_STARTED_AT, "").strip():
        if not is_demo_timed_distribution_enabled_in_settings(app_settings):
            upsert_app_settings_batch(
                connection,
                {DEMO_DISTRIBUTION_ENABLED: "1"},
            )
        return

    started_at = datetime.now().replace(microsecond=0)
    expires_at = started_at + timedelta(hours=DEMO_DISTRIBUTION_DURATION_HOURS)
    upsert_app_settings_batch(
        connection,
        {
            DEMO_DISTRIBUTION_ENABLED: "1",
            DEMO_STARTED_AT: started_at.isoformat(timespec="seconds"),
            DEMO_EXPIRES_AT: expires_at.isoformat(timespec="seconds"),
        },
    )
