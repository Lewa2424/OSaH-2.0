from pathlib import Path

from osah.application.services.security.security_setting_keys import (
    AUTH_CONFIGURED,
    INSPECTOR_PASSWORD_HASH,
    INSPECTOR_PASSWORD_SALT,
    MANAGER_PASSWORD_HASH,
    MANAGER_PASSWORD_SALT,
)
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.build_secret_hash_pair import build_secret_hash_pair
from osah.domain.services.security.validate_single_program_access_password import (
    validate_single_program_access_password,
)
from osah.domain.services.security.verify_secret_value import verify_secret_value
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


# ###### ЗМІНА ПАРОЛЯ ДОСТУПУ РОЛІ / CHANGE PROGRAM ACCESS PASSWORD ######
def change_program_access_password(
    database_path: Path,
    access_role: AccessRole,
    current_password: str,
    new_password: str,
) -> None:
    """Змінює пароль поточної ролі після перевірки поточного пароля.
    Changes the current role password after verifying the current one.
    """

    if access_role not in (AccessRole.INSPECTOR, AccessRole.MANAGER):
        raise ValueError("Невідома роль для зміни пароля.")

    role_label = "інспектора" if access_role == AccessRole.INSPECTOR else "керівника"
    normalized_new_password = validate_single_program_access_password(new_password, role_label)

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
        if app_settings.get(AUTH_CONFIGURED, "0") != "1":
            raise ValueError("Контур безпеки ще не налаштований.")

        if access_role == AccessRole.INSPECTOR:
            password_salt = app_settings.get(INSPECTOR_PASSWORD_SALT, "")
            password_hash = app_settings.get(INSPECTOR_PASSWORD_HASH, "")
            other_salt = app_settings.get(MANAGER_PASSWORD_SALT, "")
            other_hash = app_settings.get(MANAGER_PASSWORD_HASH, "")
            salt_key = INSPECTOR_PASSWORD_SALT
            hash_key = INSPECTOR_PASSWORD_HASH
        else:
            password_salt = app_settings.get(MANAGER_PASSWORD_SALT, "")
            password_hash = app_settings.get(MANAGER_PASSWORD_HASH, "")
            other_salt = app_settings.get(INSPECTOR_PASSWORD_SALT, "")
            other_hash = app_settings.get(INSPECTOR_PASSWORD_HASH, "")
            salt_key = MANAGER_PASSWORD_SALT
            hash_key = MANAGER_PASSWORD_HASH

        if not password_salt or not password_hash:
            raise ValueError("Пароль для цієї ролі ще не налаштований.")
        if not verify_secret_value(current_password, password_salt, password_hash):
            raise ValueError("Невірний поточний пароль.")
        if verify_secret_value(normalized_new_password, other_salt, other_hash):
            raise ValueError("Паролі інспектора і керівника повинні відрізнятися.")

        new_salt, new_hash = build_secret_hash_pair(normalized_new_password)
        upsert_app_settings_batch(
            connection,
            {
                salt_key: new_salt,
                hash_key: new_hash,
            },
        )
        insert_audit_log(
            connection,
            event_type="security.password_changed",
            module_name="security",
            event_level="info",
            actor_name=access_role.value,
            entity_name=access_role.value,
            result_status="success",
            description_text=f"Password changed for role {access_role.value}.",
        )
        connection.commit()
    finally:
        connection.close()
