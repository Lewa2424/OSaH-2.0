"""
Qt Login Screen - екран входу до застосунку.
Qt Login Screen - экран входа в приложение.
"""
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QRadioButton, QButtonGroup
)
from PySide6.QtGui import QFont

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.build_service_reset_request import build_service_reset_request
from osah.application.services.security.authenticate_program_access import authenticate_program_access
from osah.domain.entities.access_role import AccessRole
from osah.ui.qt.design.tokens import COLOR


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

        self.setStyleSheet(f"background-color: {COLOR['bg_app']};")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Будує інтерфейс екрана входу."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(14)

        # ---- Ліва панель ----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(28, 28, 28, 28)
        left_layout.setSpacing(20)

        title = QLabel("Вхід до локального контуру")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        left_layout.addWidget(title)

        description = QLabel(
            "Робочий shell відкривається тільки після локальної автентифікації. "
            "Інспектор отримує повний доступ, керівник працює у режимі перегляду."
        )
        description.setFont(QFont("Segoe UI", 10))
        description.setStyleSheet(f"color: {COLOR['text_muted']};")
        description.setWordWrap(True)
        left_layout.addWidget(description)

        info_card = self._create_info_card(
            "Локальна установка",
            f"ID: {self._service_reset_request.installation_id}\n"
            f"Запит: {self._service_reset_request.request_counter}"
        )
        left_layout.addWidget(info_card)

        left_layout.addStretch()
        left_card = self._create_card(left_panel)
        main_layout.addWidget(left_card, 5)

        # ---- Права панель ----
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(28, 28, 28, 28)
        right_layout.setSpacing(18)

        form_title = QLabel("Авторизація")
        form_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        form_title.setStyleSheet(f"color: {COLOR['text_primary']};")
        right_layout.addWidget(form_title)

        role_label = QLabel("Роль доступу")
        role_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        role_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        right_layout.addWidget(role_label)

        role_layout = QHBoxLayout()
        self._inspector_radio = QRadioButton("Інспектор")
        self._inspector_radio.setChecked(True)
        self._inspector_radio.setFont(QFont("Segoe UI", 11))
        self._manager_radio = QRadioButton("Керівник")
        self._manager_radio.setFont(QFont("Segoe UI", 11))
        role_layout.addWidget(self._inspector_radio)
        role_layout.addWidget(self._manager_radio)
        role_layout.addStretch()
        right_layout.addLayout(role_layout)

        password_label = QLabel("Пароль")
        password_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        password_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        right_layout.addWidget(password_label)

        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setMinimumHeight(38)
        self._password_input.setStyleSheet(self._get_input_stylesheet())
        self._password_input.returnPressed.connect(self._on_login_clicked)
        right_layout.addWidget(self._password_input)

        right_layout.addSpacing(12)

        login_button = QPushButton("Увійти")
        login_button.setMinimumHeight(40)
        login_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        login_button.setStyleSheet(self._get_button_stylesheet())
        login_button.clicked.connect(self._on_login_clicked)
        right_layout.addWidget(login_button)

        recovery_button = QPushButton("Відновити доступ")
        recovery_button.setMinimumHeight(40)
        recovery_button.setFont(QFont("Segoe UI", 11))
        recovery_button.setStyleSheet(self._get_secondary_button_stylesheet())
        recovery_button.clicked.connect(self._on_recovery_clicked)
        right_layout.addWidget(recovery_button)

        right_layout.addStretch()
        right_card = self._create_card(right_panel)
        main_layout.addWidget(right_card, 6)

    def _on_login_clicked(self) -> None:
        """Обробник натиснення кнопки входу."""
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
        """Обробник кнопки відновлення доступу."""
        self._on_recovery_requested()

    def _create_card(self, content: QWidget) -> QFrame:
        """Створює карточку з фоном."""
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {COLOR['bg_card']}; "
            f"border-radius: 20px; "
            f"border: 1px solid {COLOR['border_soft']};"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(content)
        return card

    def _create_info_card(self, title: str, value: str) -> QFrame:
        """Створює інформаційну карточку."""
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {COLOR['bg_panel']}; "
            f"border-radius: 12px; "
            f"border: 1px solid {COLOR['border_soft']};"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 10))
        value_label.setStyleSheet(f"color: {COLOR['text_primary']};")
        value_label.setWordWrap(True)
        layout.addWidget(value_label)

        return card

    def _get_input_stylesheet(self) -> str:
        """Повертає stylesheet для input-полів."""
        return (
            f"QLineEdit {{ background-color: {COLOR['bg_card']}; color: {COLOR['text_primary']}; "
            f"border: 1px solid {COLOR['border_soft']}; border-radius: 12px; padding: 0 8px; font: 11pt 'Segoe UI'; }} "
            f"QLineEdit:focus {{ border: 2px solid {COLOR['accent']}; }}"
        )

    def _get_button_stylesheet(self) -> str:
        """Повертає stylesheet для основних кнопок."""
        return (
            f"QPushButton {{ background-color: {COLOR['accent']}; color: {COLOR['accent_text']}; "
            f"border: 1px solid {COLOR['accent']}; border-radius: 15px; font: bold 11pt 'Segoe UI'; }} "
            f"QPushButton:hover {{ background-color: {COLOR['accent_hover']}; border: 1px solid {COLOR['accent_hover']}; }}"
        )

    def _get_secondary_button_stylesheet(self) -> str:
        """Повертає stylesheet для вторинних кнопок."""
        return (
            f"QPushButton {{ background-color: {COLOR['bg_card']}; color: {COLOR['text_primary']}; "
            f"border: 1px solid {COLOR['border_soft']}; border-radius: 15px; font: 11pt 'Segoe UI'; }} "
            f"QPushButton:hover {{ background-color: {COLOR['bg_panel']}; }}"
        )
