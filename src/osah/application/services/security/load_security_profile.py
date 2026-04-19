from pathlib import Path

from osah.domain.entities.security_profile import SecurityProfile
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings

from osah.application.services.security.security_setting_keys import (
    AUTH_CONFIGURED,
    FAILED_ATTEMPT_COUNT,
    INSTALLATION_ID,
    LOCKED_UNTIL,
    RECOVERY_CREATED_AT,
    RECOVERY_FILE_PATH,
    SERVICE_REQUEST_COUNTER,
)


# ###### ЗАВАНТАЖЕННЯ ПРОФІЛЮ БЕЗПЕКИ / ЗАГРУЗКА ПРОФИЛЯ БЕЗОПАСНОСТИ ######
def load_security_profile(database_path: Path) -> SecurityProfile:
    """Повертає актуальний профіль безпеки локальної установки.
    Возвращает актуальный профиль безопасности локальной установки.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    return SecurityProfile(
        installation_id=app_settings.get(INSTALLATION_ID, ""),
        is_configured=app_settings.get(AUTH_CONFIGURED, "0") == "1",
        failed_attempt_count=int(app_settings.get(FAILED_ATTEMPT_COUNT, "0") or "0"),
        locked_until_text=app_settings.get(LOCKED_UNTIL, ""),
        service_request_counter=int(app_settings.get(SERVICE_REQUEST_COUNTER, "1") or "1"),
        recovery_file_path=app_settings.get(RECOVERY_FILE_PATH, ""),
        recovery_created_at_text=app_settings.get(RECOVERY_CREATED_AT, ""),
    )
