"""
Примусова світла тема застосунку незалежно від теми Windows.
Forces a light application theme regardless of the Windows system theme.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from osah.ui.qt.design.tokens import COLOR


def build_light_application_palette() -> QPalette:
    """Будує світлу палітру Qt з дизайн-токенів ClearWork.
    Builds a light Qt palette from ClearWork design tokens.
    """
    palette = QPalette()
    color_roles = {
        QPalette.ColorRole.Window: "bg_app",
        QPalette.ColorRole.WindowText: "text_primary",
        QPalette.ColorRole.Base: "input_bg",
        QPalette.ColorRole.AlternateBase: "table_row_alt_bg",
        QPalette.ColorRole.Text: "text_primary",
        QPalette.ColorRole.Button: "button_secondary_bg",
        QPalette.ColorRole.ButtonText: "text_primary",
        QPalette.ColorRole.Highlight: "selection_bg",
        QPalette.ColorRole.HighlightedText: "text_primary",
        QPalette.ColorRole.Accent: "selection_bg",
        QPalette.ColorRole.ToolTipBase: "bg_card",
        QPalette.ColorRole.ToolTipText: "text_primary",
        QPalette.ColorRole.PlaceholderText: "input_placeholder",
        QPalette.ColorRole.Link: "accent",
        QPalette.ColorRole.Light: "bg_card",
        QPalette.ColorRole.Mid: "border_default",
        QPalette.ColorRole.Dark: "text_primary",
    }
    disabled_roles = {
        QPalette.ColorRole.Text: "input_disabled_text",
        QPalette.ColorRole.WindowText: "input_disabled_text",
        QPalette.ColorRole.ButtonText: "input_disabled_text",
        QPalette.ColorRole.Base: "input_disabled_bg",
        QPalette.ColorRole.Button: "button_disabled_bg",
    }

    for role, token_key in color_roles.items():
        color = QColor(COLOR[token_key])
        palette.setColor(QPalette.ColorGroup.Active, role, color)
        palette.setColor(QPalette.ColorGroup.Inactive, role, color)
        if role not in disabled_roles:
            palette.setColor(QPalette.ColorGroup.Disabled, role, color)

    for role, token_key in disabled_roles.items():
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(COLOR[token_key]))

    return palette


def configure_light_application_theme(application: QApplication) -> None:
    """Фіксує світлу тему застосунку і не дає Qt підхоплювати темну тему ОС.
    Pins the application to a light theme and prevents Qt from following the OS dark theme.
    """
    application.styleHints().setColorScheme(Qt.ColorScheme.Light)
    application.setPalette(build_light_application_palette())
