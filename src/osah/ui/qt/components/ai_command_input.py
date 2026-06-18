from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QWidget

from osah.ui.qt.components.ai_ui_metrics import (
    AI_CONTROL_BORDER,
    AI_CONTROL_GAP,
    AI_ICON_BUTTON_SIZE,
    AI_INPUT_HEIGHT,
)
from osah.ui.qt.design.tokens import COLOR


def _control_border(color_key: str) -> str:
    return f"{AI_CONTROL_BORDER} solid {COLOR[color_key]}"


class AiCommandInput(QWidget):
    """Поле введення AI-команди.
    AI command input field.
    """

    command_submitted = Signal(str)

    def __init__(self, parent: QWidget | None = None, *, panel_mode: bool = False) -> None:
        super().__init__(parent)
        self._panel_mode = panel_mode
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AI_CONTROL_GAP)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Скажіть команду…")
        if panel_mode:
            self._input.setMinimumWidth(0)
            self._input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self._input.setMinimumWidth(280)
        self._input.setFixedHeight(AI_INPUT_HEIGHT)
        self._input.setStyleSheet(
            f"QLineEdit {{ background: {COLOR['input_bg']}; color: {COLOR['input_text']}; "
            f"border: {_control_border('input_border')}; border-radius: 10px; padding: 0 12px; font-size: 15px; }}"
        )
        self._input.returnPressed.connect(self._submit_current_command)
        layout.addWidget(self._input)

        self._submit_button = QPushButton("▶")
        self._submit_button.setFixedSize(AI_ICON_BUTTON_SIZE, AI_ICON_BUTTON_SIZE)
        self._submit_button.setStyleSheet(
            f"QPushButton {{ background: {COLOR['button_primary_bg']}; color: {COLOR['button_primary_text']}; "
            f"border: {_control_border('button_primary_border')}; border-radius: 10px; font-size: 15px; font-weight: 700; }}"
            f"QPushButton:hover {{ background: {COLOR['button_primary_hover']}; }}"
        )
        self._submit_button.clicked.connect(self._submit_current_command)
        layout.addWidget(self._submit_button)

        if not panel_mode:
            focus_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
            focus_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            focus_shortcut.activated.connect(self.focus_input)

    def focus_input(self) -> None:
        """Переводить фокус у поле AI-команди.
        Moves focus to the AI command input field.
        """

        self._input.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self._input.selectAll()

    def set_enabled(self, enabled: bool) -> None:
        """Вмикає або вимикає введення команди.
        Enables or disables command input.
        """

        self._input.setEnabled(enabled)
        self._submit_button.setEnabled(enabled)

    def _submit_current_command(self) -> None:
        command_text = self._input.text().strip()
        if not command_text:
            return
        self.command_submitted.emit(command_text)
        self._input.clear()
