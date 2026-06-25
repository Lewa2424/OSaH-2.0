from pathlib import Path

from PySide6.QtWidgets import QApplication

from osah.application.services.load_ui_scale_preset import load_ui_scale_preset
from osah.domain.entities.ui_scale_preset import UiScalePreset
from osah.ui.qt.components.configure_light_application_theme import configure_light_application_theme
from osah.ui.qt.design.stylesheet import build_global_stylesheet
from osah.ui.qt.design.ui_scale import build_application_font, init_ui_scale


# ###### ЗАСТОСУВАННЯ ВІЗУАЛЬНОЇ ТЕМИ / APPLY APPLICATION VISUAL THEME ######
def apply_application_visual_theme(application: QApplication, database_path: Path | None) -> UiScalePreset:
    """Застосовує пресет масштабу, палітру та глобальний QSS до QApplication.
    Applies the UI scale preset, palette, and global QSS to QApplication.
    """

    ui_scale_preset = _load_ui_scale_preset_safely(database_path)
    init_ui_scale(ui_scale_preset)
    configure_light_application_theme(application)
    application.setFont(build_application_font())
    application.setStyleSheet(build_global_stylesheet())
    return ui_scale_preset


# ###### БЕЗПЕЧНЕ ЗАВАНТАЖЕННЯ ПРЕСЕТУ / LOAD PRESET SAFELY ######
def _load_ui_scale_preset_safely(database_path: Path | None) -> UiScalePreset:
    """Повертає compact, якщо БД недоступна під час раннього старту.
    Returns compact when the database is unavailable during early startup.
    """

    if database_path is None:
        return UiScalePreset.COMPACT

    try:
        return load_ui_scale_preset(database_path)
    except Exception:
        return UiScalePreset.COMPACT
