from pathlib import Path

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ui_scale_preset import UiScalePreset
from osah.domain.errors.access_denied_error import AccessDeniedError
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_app_setting import upsert_app_setting
from osah.infrastructure.database.create_database_connection import create_database_connection

_UI_SCALE_PRESET_SETTING_KEY = "ui.scale_preset"
_ALLOWED_ACCESS_ROLES = frozenset({AccessRole.INSPECTOR, AccessRole.MANAGER})


# ###### ЗБЕРЕЖЕННЯ ПРЕСЕТУ МАСШТАБУ / SAVE UI SCALE PRESET ######
def save_ui_scale_preset(
    database_path: Path,
    ui_scale_preset: UiScalePreset,
    *,
    access_role: AccessRole,
) -> None:
    """Зберігає пресет масштабу інтерфейсу для обох робочих ролей.
    Persists the UI scale preset for both inspector and manager roles.
    """

    if access_role not in _ALLOWED_ACCESS_ROLES:
        raise AccessDeniedError(
            f"Доступ заборонено: роль '{access_role}' не може змінювати масштаб інтерфейсу."
        )

    connection = create_database_connection(database_path)
    try:
        upsert_app_setting(connection, _UI_SCALE_PRESET_SETTING_KEY, ui_scale_preset.value)
        insert_audit_log(
            connection,
            event_type="settings.ui_scale_updated",
            module_name="settings",
            event_level="info",
            actor_name=access_role.value,
            entity_name="settings.ui_scale",
            result_status="success",
            description_text=f"UI scale preset updated to '{ui_scale_preset.value}'.",
        )
        connection.commit()
    finally:
        connection.close()
