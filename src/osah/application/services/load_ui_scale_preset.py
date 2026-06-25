from pathlib import Path

from osah.domain.entities.ui_scale_preset import UiScalePreset
from osah.domain.services.parse_ui_scale_preset import parse_ui_scale_preset
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings

_UI_SCALE_PRESET_SETTING_KEY = "ui.scale_preset"


# ###### ЗАВАНТАЖЕННЯ ПРЕСЕТУ МАСШТАБУ / LOAD UI SCALE PRESET ######
def load_ui_scale_preset(database_path: Path) -> UiScalePreset:
    """Читає збережений пресет масштабу інтерфейсу з app_settings.
    Reads the saved UI scale preset from app_settings.
    """

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    return parse_ui_scale_preset(app_settings.get(_UI_SCALE_PRESET_SETTING_KEY))
