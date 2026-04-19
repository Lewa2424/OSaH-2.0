from datetime import datetime, timedelta
from pathlib import Path

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.authentication_result import AuthenticationResult
from osah.domain.services.security.verify_secret_value import verify_secret_value
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings

from osah.application.services.security.security_setting_keys import (
    AUTH_CONFIGURED,
    FAILED_ATTEMPT_COUNT,
    INSPECTOR_PASSWORD_HASH,
    INSPECTOR_PASSWORD_SALT,
    INSTALLATION_ID,
    LOCKED_UNTIL,
    MANAGER_PASSWORD_HASH,
    MANAGER_PASSWORD_SALT,
)


# ###### АВТЕНТИФІКАЦІЯ ДОСТУПУ ДО ПРОГРАМИ / АУТЕНТИФИКАЦИЯ ДОСТУПА К ПРОГРАММЕ ######
def authenticate_program_access(
    database_path: Path,
    access_role: AccessRole,
    password_text: str,
) -> AuthenticationResult:
    """Перевіряє пароль ролі, тимчасове блокування і повертає результат входу.
    Проверяет пароль роли, временную блокировку и возвращает результат входа.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
        installation_id = app_settings.get(INSTALLATION_ID, "unknown")
        if app_settings.get(AUTH_CONFIGURED, "0") != "1":
            return AuthenticationResult(False, None, "Спочатку потрібно завершити первинне налаштування доступу.")

        failed_attempt_count = int(app_settings.get(FAILED_ATTEMPT_COUNT, "0") or "0")
        locked_until_text = app_settings.get(LOCKED_UNTIL, "")
        now = datetime.now()
        if locked_until_text:
            locked_until = datetime.fromisoformat(locked_until_text)
            if now < locked_until:
                return AuthenticationResult(
                    False,
                    None,
                    f"Вхід тимчасово заблоковано до {locked_until.strftime('%Y-%m-%d %H:%M:%S')}.",
                )
            failed_attempt_count = 0
            locked_until_text = ""

        password_salt = (
            app_settings.get(INSPECTOR_PASSWORD_SALT, "")
            if access_role == AccessRole.INSPECTOR
            else app_settings.get(MANAGER_PASSWORD_SALT, "")
        )
        password_hash = (
            app_settings.get(INSPECTOR_PASSWORD_HASH, "")
            if access_role == AccessRole.INSPECTOR
            else app_settings.get(MANAGER_PASSWORD_HASH, "")
        )
        is_authenticated = bool(password_salt and password_hash) and verify_secret_value(
            password_text,
            password_salt,
            password_hash,
        )

        if is_authenticated:
            upsert_app_settings_batch(connection, {FAILED_ATTEMPT_COUNT: "0", LOCKED_UNTIL: ""})
            insert_audit_log(
                connection,
                event_type="security.login_success",
                module_name="security",
                event_level="info",
                actor_name=access_role.value,
                entity_name=installation_id,
                result_status="success",
                description_text="Program login completed successfully.",
            )
            connection.commit()
            return AuthenticationResult(True, access_role, "Вхід виконано успішно.")

        failed_attempt_count += 1
        updated_setting_pairs = {FAILED_ATTEMPT_COUNT: str(failed_attempt_count), LOCKED_UNTIL: ""}
        message_text = "Невірний пароль."
        if failed_attempt_count >= 5:
            locked_until = now + timedelta(minutes=5)
            updated_setting_pairs[LOCKED_UNTIL] = locked_until.isoformat(timespec="seconds")
            message_text = f"Вхід тимчасово заблоковано до {locked_until.strftime('%Y-%m-%d %H:%M:%S')}."

        upsert_app_settings_batch(connection, updated_setting_pairs)
        insert_audit_log(
            connection,
            event_type="security.login_failed",
            module_name="security",
            event_level="warning",
            actor_name=access_role.value,
            entity_name=installation_id,
            result_status="denied",
            description_text="Program login failed.",
        )
        connection.commit()
        return AuthenticationResult(False, None, message_text)
    finally:
        connection.close()
