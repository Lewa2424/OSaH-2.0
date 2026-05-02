"""
Qt Initial Setup Screen - екран першого налаштування безпеки.
Qt Initial Setup Screen - first security setup screen.
"""

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.configure_program_access import configure_program_access
from osah.application.services.security.load_security_profile import load_security_profile
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class InitialSetupScreen(QWidget):
    """Екран первинного налаштування паролів і recovery-механіки."""

    def __init__(
        self,
        application_context: ApplicationContext,
        on_configured: Callable[[], None],
    ) -> None:
        """Ініціалізує екран. Initializes the screen."""
        super().__init__()
        self._app_context = application_context
        self._on_configured = on_configured
        self._security_profile = load_security_profile(application_context.database_path)

        self.setObjectName("initialSetupRoot")
        self.setStyleSheet(
            f"QWidget#initialSetupRoot {{ "
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 {COLOR['bg_app']}, stop:1 {COLOR['bg_workspace']}); "
            f"}}"
        )
        self._setup_ui()

    def _setup_ui(self) -> None:
        """###### ІНТЕРФЕЙС ПЕРШОГО ЗАПУСКУ / INITIAL SETUP UI ######"""

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(44, 36, 44, 36)
        root_layout.setSpacing(SPACING["lg"])
        root_layout.addStretch(1)

        content = QWidget()
        content.setMinimumWidth(960)
        content.setMaximumWidth(1120)
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING["lg"])

        content_layout.addWidget(self._build_setup_card())
        content_layout.addWidget(self._build_service_strip())

        root_layout.addWidget(content, 0, Qt.AlignmentFlag.AlignHCenter)
        root_layout.addStretch(2)

    def _build_setup_card(self) -> QFrame:
        """###### КАРТКА ПАРАМЕТРІВ / SETUP CARD ######"""

        card = self._create_shell_card("initialSetupCard")
        card.setMinimumHeight(330)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Первинне налаштування доступу")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        layout.addWidget(title)

        description = QLabel(
            "Задайте окремі локальні паролі для інспектора і керівника. "
            "Після збереження система створить recovery-файл і ввімкне локальний контур безпеки."
        )
        description.setFont(QFont("Segoe UI", 12))
        description.setStyleSheet(f"color: {COLOR['text_secondary']};")
        description.setWordWrap(True)
        layout.addWidget(description)

        input_row = QHBoxLayout()
        input_row.setSpacing(SPACING["md"])

        self._inspector_input = QLineEdit()
        self._inspector_input.setPlaceholderText("ПАРОЛЬ ІНСПЕКТОРА")
        self._inspector_input.setEchoMode(QLineEdit.Password)
        self._inspector_input.setMinimumHeight(52)
        self._inspector_input.setStyleSheet(self._get_input_stylesheet())
        input_row.addWidget(self._inspector_input, 1)

        self._manager_input = QLineEdit()
        self._manager_input.setPlaceholderText("ПАРОЛЬ КЕРІВНИКА")
        self._manager_input.setEchoMode(QLineEdit.Password)
        self._manager_input.setMinimumHeight(52)
        self._manager_input.setStyleSheet(self._get_input_stylesheet())
        self._manager_input.returnPressed.connect(self._on_save_clicked)
        input_row.addWidget(self._manager_input, 1)

        layout.addLayout(input_row)

        note = QLabel(
            "Паролі не зберігаються у відкритому вигляді. Recovery-файл потрібно тримати окремо від робочого ПК."
        )
        note.setFont(QFont("Segoe UI", 10, QFont.Bold))
        note.setStyleSheet(f"color: {COLOR['text_muted']};")
        note.setWordWrap(True)
        layout.addWidget(note)

        save_button = QPushButton("Зберегти параметри")
        save_button.setMinimumHeight(48)
        save_button.setFont(QFont("Segoe UI", 13, QFont.Bold))
        save_button.setStyleSheet(self._get_button_stylesheet())
        save_button.clicked.connect(self._on_save_clicked)
        layout.addWidget(save_button)

        self.setTabOrder(self._inspector_input, self._manager_input)
        self.setTabOrder(self._manager_input, save_button)

        return card

    def _build_service_strip(self) -> QFrame:
        """###### СЛУЖБОВА СМУГА / SERVICE STRIP ######"""

        strip = self._create_shell_card("initialSetupServiceStrip")
        strip.setMaximumHeight(140)
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(SPACING["xl"])

        text_panel = QWidget()
        text_layout = QVBoxLayout(text_panel)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)

        title = QLabel("Локальна установка")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        text_layout.addWidget(title)

        description = QLabel(
            "Службова інформація для ідентифікації установки та сценарію відновлення доступу."
        )
        description.setFont(QFont("Segoe UI", 10))
        description.setStyleSheet(f"color: {COLOR['text_secondary']};")
        description.setWordWrap(True)
        text_layout.addWidget(description)
        text_layout.addStretch()
        layout.addWidget(text_panel, 2)

        layout.addWidget(self._create_info_card("ID установки", self._security_profile.installation_id), 3)

        return strip

    def _on_save_clicked(self) -> None:
        """###### ЗБЕРЕЖЕННЯ ПАРАМЕТРІВ / SAVE SETUP PARAMETERS ######"""

        inspector_password = self._inspector_input.text()
        manager_password = self._manager_input.text()

        if not inspector_password or not manager_password:
            return

        configure_program_access(
            database_path=self._app_context.database_path,
            inspector_password=inspector_password,
            manager_password=manager_password,
        )

        self._on_configured()

    def _create_shell_card(self, object_name: str) -> QFrame:
        """###### КАРТКА ЕКРАНУ / SCREEN CARD ######"""

        card = QFrame()
        card.setObjectName(object_name)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(
            f"QFrame#{object_name} {{ "
            f"background: {COLOR['bg_card']}; "
            f"border: 1px solid {COLOR['card_border']}; "
            f"border-radius: {RADIUS['lg']}px; "
            f"}}"
        )
        return card

    def _create_info_card(self, title: str, value: str) -> QFrame:
        """###### СЛУЖБОВА КАРТКА / SERVICE INFO CARD ######"""

        card = QFrame()
        card.setObjectName("initialSetupInfoCard")
        card.setStyleSheet(
            f"QFrame#initialSetupInfoCard {{ "
            f"background: {COLOR['bg_panel']}; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['md']}px; "
            f"}}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLOR['text_primary']};")
        value_label.setWordWrap(True)
        layout.addWidget(value_label)

        return card

    def _get_input_stylesheet(self) -> str:
        """###### СТИЛЬ ПОЛЯ ВВОДУ / INPUT STYLE ######"""

        return (
            f"QLineEdit {{ "
            f"background: {COLOR['input_bg']}; "
            f"color: {COLOR['input_text']}; "
            f"border: 1px solid {COLOR['input_border']}; "
            f"border-radius: {RADIUS['md']}px; "
            f"padding: 0 16px; "
            f"font: 13pt 'Segoe UI'; "
            f"}} "
            f"QLineEdit:focus {{ border: 2px solid {COLOR['input_border_focus']}; }} "
            f"QLineEdit:disabled {{ background: {COLOR['input_disabled_bg']}; color: {COLOR['input_disabled_text']}; }}"
        )

    def _get_button_stylesheet(self) -> str:
        """###### СТИЛЬ ОСНОВНОЇ КНОПКИ / PRIMARY BUTTON STYLE ######"""

        return (
            f"QPushButton {{ "
            f"background: {COLOR['button_primary_bg']}; "
            f"color: {COLOR['button_primary_text']}; "
            f"border: 1px solid {COLOR['button_primary_border']}; "
            f"border-radius: {RADIUS['md']}px; "
            f"font: bold 13pt 'Segoe UI'; "
            f"}} "
            f"QPushButton:hover {{ background: {COLOR['button_primary_hover']}; }} "
            f"QPushButton:pressed {{ background: {COLOR['button_primary_active']}; }}"
        )
