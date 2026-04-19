from datetime import datetime
from pathlib import Path

from osah.domain.entities.program_access_reset_result import ProgramAccessResetResult
from osah.domain.services.security.build_secret_hash_pair import build_secret_hash_pair
from osah.domain.services.security.generate_recovery_code import generate_recovery_code
from osah.domain.services.security.validate_program_access_passwords import validate_program_access_passwords
from osah.domain.services.security.verify_secret_value import verify_secret_value
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.infrastructure.security.build_recovery_file_content import build_recovery_file_content
from osah.infrastructure.security.build_recovery_file_path import build_recovery_file_path
from osah.infrastructure.security.write_recovery_file import write_recovery_file

from osah.application.services.security.security_setting_keys import (
    AUTH_CONFIGURED,
    FAILED_ATTEMPT_COUNT,
    INSPECTOR_PASSWORD_HASH,
    INSPECTOR_PASSWORD_SALT,
    INSTALLATION_ID,
    LOCKED_UNTIL,
    MANAGER_PASSWORD_HASH,
    MANAGER_PASSWORD_SALT,
    RECOVERY_CODE_HASH,
    RECOVERY_CODE_SALT,
    RECOVERY_CREATED_AT,
    RECOVERY_FILE_PATH,
)


# ###### СКИДАННЯ ДОСТУПУ ЧЕРЕЗ RECOVERY-КОД / СБРОС ДОСТУПА ЧЕРЕЗ RECOVERY-КОД ######
def reset_program_access_with_recovery_code(
    database_path: Path,
    recovery_code: str,
    new_inspector_password: str,
    new_manager_password: str,
) -> ProgramAccessResetResult:
    """Скидає паролі через recovery-код і випускає новий recovery-файл.
    Сбрасывает пароли через recovery-код и выпускает новый recovery-файл.
    """

    validate_program_access_passwords(new_inspector_password, new_manager_password)
    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
        installation_id = app_settings.get(INSTALLATION_ID, "unknown")
        if app_settings.get(AUTH_CONFIGURED, "0") != "1":
            raise ValueError("Контур безпеки ще не налаштований.")

        recovery_code_salt = app_settings.get(RECOVERY_CODE_SALT, "")
        recovery_code_hash = app_settings.get(RECOVERY_CODE_HASH, "")
        if not recovery_code_salt or not recovery_code_hash or not verify_secret_value(
            recovery_code,
            recovery_code_salt,
            recovery_code_hash,
        ):
            insert_audit_log(
                connection,
                event_type="security.recovery_code_failed",
                module_name="security",
                event_level="warning",
                actor_name="recovery",
                entity_name=installation_id,
                result_status="denied",
                description_text="Recovery code validation failed.",
            )
            connection.commit()
            raise ValueError("Невірний recovery-код.")

        new_recovery_code = generate_recovery_code()
        recovery_file_path = build_recovery_file_path(database_path, installation_id)
        recovery_created_at_text = datetime.now().isoformat(timespec="seconds")
        inspector_password_salt, inspector_password_hash = build_secret_hash_pair(new_inspector_password)
        manager_password_salt, manager_password_hash = build_secret_hash_pair(new_manager_password)
        new_recovery_code_salt, new_recovery_code_hash = build_secret_hash_pair(new_recovery_code)

        write_recovery_file(
            recovery_file_path,
            build_recovery_file_content(installation_id, new_recovery_code, recovery_created_at_text),
        )
        upsert_app_settings_batch(
            connection,
            {
                INSPECTOR_PASSWORD_HASH: inspector_password_hash,
                INSPECTOR_PASSWORD_SALT: inspector_password_salt,
                MANAGER_PASSWORD_HASH: manager_password_hash,
                MANAGER_PASSWORD_SALT: manager_password_salt,
                RECOVERY_CODE_HASH: new_recovery_code_hash,
                RECOVERY_CODE_SALT: new_recovery_code_salt,
                FAILED_ATTEMPT_COUNT: "0",
                LOCKED_UNTIL: "",
                RECOVERY_FILE_PATH: str(recovery_file_path),
                RECOVERY_CREATED_AT: recovery_created_at_text,
            },
        )
        insert_audit_log(
            connection,
            event_type="security.recovery_code_used",
            module_name="security",
            event_level="warning",
            actor_name="recovery",
            entity_name=installation_id,
            result_status="success",
            description_text="Access reset completed using recovery code.",
        )
        connection.commit()
        return ProgramAccessResetResult(new_recovery_code, recovery_file_path)
    finally:
        connection.close()
