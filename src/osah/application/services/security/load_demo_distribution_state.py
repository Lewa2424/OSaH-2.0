from datetime import datetime
from pathlib import Path

from osah.application.services.security.is_demo_timed_distribution_active import is_demo_timed_distribution_active
from osah.application.services.security.security_setting_keys import DEMO_EXPIRES_AT, DEMO_STARTED_AT
from osah.domain.entities.demo_distribution_state import DemoDistributionState
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


_INACTIVE_STATE = DemoDistributionState(
    is_active=False,
    is_expired=False,
    started_at=None,
    expires_at=None,
    remaining_seconds=0,
)


# ###### ЗАВАНТАЖЕННЯ СТАНУ DEMO-ДИСТРИБУЦІЇ / LOAD DEMO DISTRIBUTION STATE ######
def load_demo_distribution_state(database_path: Path, *, now: datetime | None = None) -> DemoDistributionState:
    """Повертає стан timed demo для UI та перевірок доступу.
    Returns timed demo state for UI and access checks.
    """

    if not is_demo_timed_distribution_active(database_path):
        return _INACTIVE_STATE

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    started_at = _parse_timestamp(app_settings.get(DEMO_STARTED_AT, ""))
    expires_at = _parse_timestamp(app_settings.get(DEMO_EXPIRES_AT, ""))
    if started_at is None or expires_at is None:
        return DemoDistributionState(
            is_active=True,
            is_expired=False,
            started_at=started_at,
            expires_at=expires_at,
            remaining_seconds=0,
        )

    current_time = now if now is not None else datetime.now().replace(microsecond=0)
    remaining_seconds = max(0, int((expires_at - current_time).total_seconds()))
    return DemoDistributionState(
        is_active=True,
        is_expired=current_time >= expires_at,
        started_at=started_at,
        expires_at=expires_at,
        remaining_seconds=remaining_seconds,
    )


def _parse_timestamp(raw_value: str) -> datetime | None:
    normalized = raw_value.strip()
    if not normalized:
        return None
    return datetime.fromisoformat(normalized)
