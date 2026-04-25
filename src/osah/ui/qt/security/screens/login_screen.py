"""
Qt Login Screen - екран входу до застосунку.
Qt Login Screen - application login screen.
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
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.application.services.security.build_service_reset_request import build_service_reset_request
from osah.domain.entities.access_role import AccessRole
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class LoginScreen(QWidget):
    """Екран входу з вибором ролі та введенням пароля."""

    def __init__(
        self,
        application_context: ApplicationContext,
        on_authenticated: Callable[[AccessRole], None],
        on_recovery_requested: Callable[[], None],
    ) -> None:
        super().__init__()
        self._app_context = application_context
        self._on_authenticated = on_authenticated
        self._on_recovery_requested = on_recovery_requested
        self._service_reset_request = build_service_reset_request(application_context.database_path)

        self.setObjectName("loginScreenRoot")
        self.setStyleSheet(
            f"QWidget#loginScreenRoot {{ "
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 {COLOR['bg_app']}, stop:1 {COLOR['bg_workspace']}); "
            f"}}"
        )
        self._setup_ui()

    def _setup_ui(self) -> None:
        """###### ІНТЕРФЕЙС ВХОДУ / LOGIN UI ######"""

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(44, 36, 44, 36)
        root_layout.setSpacing(SPACING["lg"])
        root_layout.addStretch(1)

        content = QWidget()
        content.setObjectName("loginContent")
        content.setMinimumWidth(960)
        content.setMaximumWidth(1120)
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING["lg"])

        content_layout.addWidget(self._build_auth_card())
        content_layout.addWidget(self._build_service_strip())

        root_layout.addWidget(content, 0, Qt.AlignmentFlag.AlignHCenter)
        root_layout.addStretch(2)

    def _build_auth_card(self) -> QFrame:
        """###### КАРТКА АВТОРИЗАЦІЇ / AUTHORIZATION CARD ######"""

        card = self._create_shell_card("loginAuthCard")
        card.setMinimumHeight(330)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Авторизація")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        layout.addWidget(title)

        description = QLabel(
            "Вхід до локального контуру відкриває робочий shell. "
            "Інспектор отримує повний доступ, керівник працює у режимі перегляду."
        )
        description.setFont(QFont("Segoe UI", 12))
        description.setStyleSheet(f"color: {COLOR['text_secondary']};")
        description.setWordWrap(True)
        layout.addWidget(description)

        role_label = QLabel("Роль доступу")
        role_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        role_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(role_label)

        role_layout = QHBoxLayout()
        role_layout.setSpacing(28)
        self._inspector_radio = QRadioButton("Інспектор")
        self._inspector_radio.setChecked(True)
        self._inspector_radio.setFont(QFont("Segoe UI", 13))
        self._manager_radio = QRadioButton("Керівник")
        self._manager_radio.setFont(QFont("Segoe UI", 13))
        role_layout.addWidget(self._inspector_radio)
        role_layout.addWidget(self._manager_radio)
        role_layout.addStretch()
        layout.addLayout(role_layout)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("ВВЕДІТЬ ПАРОЛЬ")
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setMinimumHeight(52)
        self._password_input.setStyleSheet(self._get_input_stylesheet())
        self._password_input.returnPressed.connect(self._on_login_clicked)
        layout.addWidget(self._password_input)

        button_row = QHBoxLayout()
        button_row.setSpacing(SPACING["md"])

        login_button = QPushButton("Увійти")
        login_button.setMinimumHeight(48)
        login_button.setFont(QFont("Segoe UI", 13, QFont.Bold))
        login_button.setStyleSheet(self._get_button_stylesheet())
        login_button.clicked.connect(self._on_login_clicked)
        button_row.addWidget(login_button, 2)

        recovery_button = QPushButton("Відновити доступ")
        recovery_button.setMinimumHeight(48)
        recovery_button.setFont(QFont("Segoe UI", 12))
        recovery_button.setStyleSheet(self._get_secondary_button_stylesheet())
        recovery_button.clicked.connect(self._on_recovery_clicked)
        button_row.addWidget(recovery_button, 1)

        layout.addLayout(button_row)

        self.setTabOrder(self._inspector_radio, self._manager_radio)
        self.setTabOrder(self._manager_radio, self._password_input)
        self.setTabOrder(self._password_input, login_button)
        self.setTabOrder(login_button, recovery_button)

        return card

    def _build_service_strip(self) -> QFrame:
        """###### СЛУЖБОВА СМУГА / SERVICE STRIP ######"""

        strip = self._create_shell_card("loginServiceStrip")
        strip.setMaximumHeight(150)
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

        installation_card = self._create_info_card(
            "ID установки",
            self._service_reset_request.installation_id,
        )
        layout.addWidget(installation_card, 3)

        request_card = self._create_info_card(
            "Запит",
            str(self._service_reset_request.request_counter),
        )
        layout.addWidget(request_card, 1)

        return strip

    def _on_login_clicked(self) -> None:
        """###### ВХІД ДО ПРОГРАМИ / PROGRAM LOGIN ######"""

        access_role = AccessRole.INSPECTOR if self._inspector_radio.isChecked() else AccessRole.MANAGER
        password = self._password_input.text()

        if not password:
            return

        result = authenticate_program_access(
            database_path=self._app_context.database_path,
            access_role=access_role,
            password_text=password,
        )

        if result.is_authenticated and result.access_role:
            self._on_authenticated(result.access_role)

    def _on_recovery_clicked(self) -> None:
        """###### ВІДНОВЛЕННЯ ДОСТУПУ / ACCESS RECOVERY ######"""

        self._on_recovery_requested()

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
        card.setObjectName("loginInfoCard")
        card.setStyleSheet(
            f"QFrame#loginInfoCard {{ "
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

    def _get_secondary_button_stylesheet(self) -> str:
        """###### СТИЛЬ ДРУГОРЯДНОЇ КНОПКИ / SECONDARY BUTTON STYLE ######"""

        return (
            f"QPushButton {{ "
            f"background: {COLOR['button_secondary_bg']}; "
            f"color: {COLOR['button_secondary_text']}; "
            f"border: 1px solid {COLOR['button_secondary_border']}; "
            f"border-radius: {RADIUS['md']}px; "
            f"font: 12pt 'Segoe UI'; "
            f"}} "
            f"QPushButton:hover {{ background: {COLOR['button_secondary_hover']}; }} "
            f"QPushButton:pressed {{ background: {COLOR['button_secondary_active']}; }}"
        )
