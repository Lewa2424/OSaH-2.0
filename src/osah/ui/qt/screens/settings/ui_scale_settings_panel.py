from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.ui_scale_preset import UiScalePreset
from osah.domain.services.format_ui_scale_preset_label import format_ui_scale_preset_presentation
from osah.ui.qt.components.app_dialog import AppDialogAction, AppDialogIcon, show_app_dialog
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class UiScaleSettingsPanel(SettingsSectionCard):
    """Секція вибору масштабу інтерфейсу ClearWork.
    Settings section for ClearWork UI scale presets.
    """

    save_requested = Signal(UiScalePreset)

    def __init__(self, ui_scale_preset: UiScalePreset) -> None:
        super().__init__()
        self._saved_preset = ui_scale_preset
        self._tile_buttons: dict[UiScalePreset, QPushButton] = {}

        layout = self.content_layout()
        title = QLabel("Масштабування")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        subtitle = QLabel("Оберіть зручний розмір тексту та елементів інтерфейсу.")
        subtitle.setProperty("role", "section_header_subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        grid_host = QWidget()
        grid_layout = QGridLayout(grid_host)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(SPACING["md"])
        grid_layout.setVerticalSpacing(SPACING["md"])

        for index, preset in enumerate(UiScalePreset):
            tile_button = self._build_tile_button(preset)
            self._tile_buttons[preset] = tile_button
            grid_layout.addWidget(tile_button, index // 2, index % 2)

        layout.addWidget(grid_host)
        self._apply_selection(self._saved_preset)

    # ###### ПЛИТКА ПРЕСЕТУ / BUILD PRESET TILE ######
    def _build_tile_button(self, preset: UiScalePreset) -> QPushButton:
        """Створює кнопку-плитку для одного пресету масштабу.
        Builds a tile button for a single UI scale preset.
        """

        presentation = format_ui_scale_preset_presentation(preset)
        hint_text = f"\n{presentation.hint}" if presentation.hint else ""
        tile_button = QPushButton(f"{presentation.title}{hint_text}")
        tile_button.setProperty("variant", "secondary")
        tile_button.setProperty("ui_scale_tile", "true")
        tile_button.setCheckable(True)
        tile_button.setMinimumHeight(88)
        tile_button.clicked.connect(lambda _checked=False, selected_preset=preset: self._on_tile_clicked(selected_preset))
        return tile_button

    # ###### ОБРОБКА ВИБОРУ ПЛИТКИ / HANDLE TILE CLICK ######
    def _on_tile_clicked(self, selected_preset: UiScalePreset) -> None:
        """Підтверджує зміну масштабу або повертає попередній вибір.
        Confirms the scale change or restores the previous selection.
        """

        if selected_preset == self._saved_preset:
            self._apply_selection(self._saved_preset)
            return

        self._apply_selection(selected_preset)
        confirmed = show_app_dialog(
            self,
            window_title="Масштабування",
            message="Програму буде перезапущено для застосування масштабу. Продовжити?",
            icon=AppDialogIcon.QUESTION,
            actions=(
                AppDialogAction("no", "Ні", "secondary"),
                AppDialogAction("yes", "Так", "accent"),
            ),
            default_action_id="yes",
        )
        if confirmed == "yes":
            self.save_requested.emit(selected_preset)
            return

        self._apply_selection(self._saved_preset)

    # ###### ОНОВЛЕННЯ АКТИВНОЇ ПЛИТКИ / APPLY TILE SELECTION ######
    def _apply_selection(self, preset: UiScalePreset) -> None:
        """Підсвічує активний пресет на сітці 2x2.
        Highlights the active preset on the 2x2 tile grid.
        """

        for tile_preset, tile_button in self._tile_buttons.items():
            is_selected = tile_preset == preset
            tile_button.setChecked(is_selected)
            tile_button.setStyleSheet(_build_tile_style(is_selected))

    # ###### ПІДТВЕРДЖЕННЯ ЗБЕРЕЖЕННЯ / MARK PRESET SAVED ######
    def mark_preset_saved(self, preset: UiScalePreset) -> None:
        """Оновлює збережений пресет після успішного запису в БД.
        Updates the saved preset after a successful database write.
        """

        self._saved_preset = preset
        self._apply_selection(preset)


# ###### СТИЛЬ ПЛИТКИ МАСШТАБУ / BUILD TILE STYLE ######
def _build_tile_style(is_selected: bool) -> str:
    """Повертає QSS для плитки пресету масштабу.
    Returns QSS for a UI scale preset tile.
    """

    if is_selected:
        return (
            f"background: {COLOR['accent_soft']};"
            f" color: {COLOR['accent']};"
            f" border: 2px solid {COLOR['accent']};"
            " font-weight: 700;"
            " text-align: center;"
        )
    return (
        f"background: {COLOR['button_secondary_bg']};"
        f" color: {COLOR['text_primary']};"
        f" border: 1px solid {COLOR['button_secondary_border']};"
        " font-weight: 600;"
        " text-align: center;"
    )
