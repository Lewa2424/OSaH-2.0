from pathlib import Path

from osah.domain.services.security.generate_installation_id import generate_installation_id
from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
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


# ###### ЗАБЕЗПЕЧЕННЯ БАЗОВОГО ПРОФІЛЮ БЕЗПЕКИ / ОБЕСПЕЧЕНИЕ БАЗОВОГО ПРОФИЛЯ БЕЗОПАСНОСТИ ######
def ensure_security_baseline(database_path: Path) -> None:
    """Створює базові security-налаштування для нової локальної установки.
    Создаёт базовые security-настройки для новой локальной установки.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
        default_setting_pairs: dict[str, str] = {}
        if not app_settings.get(INSTALLATION_ID):
            default_setting_pairs[INSTALLATION_ID] = generate_installation_id()
        if AUTH_CONFIGURED not in app_settings:
            default_setting_pairs[AUTH_CONFIGURED] = "0"
        if FAILED_ATTEMPT_COUNT not in app_settings:
            default_setting_pairs[FAILED_ATTEMPT_COUNT] = "0"
        if LOCKED_UNTIL not in app_settings:
            default_setting_pairs[LOCKED_UNTIL] = ""
        if SERVICE_REQUEST_COUNTER not in app_settings:
            default_setting_pairs[SERVICE_REQUEST_COUNTER] = "1"
        if RECOVERY_FILE_PATH not in app_settings:
            default_setting_pairs[RECOVERY_FILE_PATH] = ""
        if RECOVERY_CREATED_AT not in app_settings:
            default_setting_pairs[RECOVERY_CREATED_AT] = ""

        if default_setting_pairs:
            upsert_app_settings_batch(connection, default_setting_pairs)
            connection.commit()
    finally:
        connection.close()
