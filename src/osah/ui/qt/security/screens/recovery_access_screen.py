"""
Qt Recovery Access Screen - екран відновлення доступу.
"""
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTabWidget
)
from PySide6.QtGui import QFont

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.build_service_reset_request import build_service_reset_request
from osah.application.services.security.reset_program_access_with_recovery_code import reset_program_access_with_recovery_code
from osah.application.services.security.reset_program_access_with_service_code import reset_program_access_with_service_code
from osah.ui.qt.design.tokens import COLOR


class RecoveryAccessScreen(QWidget):
    """Екран відновлення доступу через recovery-код або service-код."""

    def __init__(
        self,
        application_context: ApplicationContext,
        on_finished: Callable[[], None],
        on_back_to_login: Callable[[], None],
    ) -> None:
        super().__init__()
        self._app_context = application_context
        self._on_finished = on_finished
        self._on_back_to_login = on_back_to_login
        self._service_reset_request = build_service_reset_request(application_context.database_path)

        self.setStyleSheet(f"background-color: {COLOR['bg_app']};")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Будує інтерфейс екрана відновлення."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(14)

        # ---- Ліва панель ----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(28, 28, 28, 28)
        left_layout.setSpacing(20)

        title = QLabel("Аварійне відновлення доступу")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        left_layout.addWidget(title)

        description = QLabel(
            "Recovery-код для власника. Сервісний код видається окремо під ID установки."
        )
        description.setFont(QFont("Segoe UI", 10))
        description.setStyleSheet(f"color: {COLOR['text_muted']};")
        description.setWordWrap(True)
        left_layout.addWidget(description)

        info_card = self._create_info_card(
            "Реквізити",
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

        form_title = QLabel("Скидання паролів")
        form_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        form_title.setStyleSheet(f"color: {COLOR['text_primary']};")
        right_layout.addWidget(form_title)

        # Tab widget
        tabs = QTabWidget()

        # Recovery tab
        recovery_tab = QWidget()
        recovery_layout = QVBoxLayout(recovery_tab)
        recovery_layout.setSpacing(12)

        recovery_code_label = QLabel("Recovery-код")
        recovery_code_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        recovery_layout.addWidget(recovery_code_label)

        self._recovery_code_input = QLineEdit()
        self._recovery_code_input.setMinimumHeight(38)
        self._recovery_code_input.setStyleSheet(self._get_input_stylesheet())
        recovery_layout.addWidget(self._recovery_code_input)

        recovery_inspector_label = QLabel("Пароль інспектора")
        recovery_inspector_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        recovery_layout.addWidget(recovery_inspector_label)

        self._recovery_inspector_input = QLineEdit()
        self._recovery_inspector_input.setEchoMode(QLineEdit.Password)
        self._recovery_inspector_input.setMinimumHeight(38)
        self._recovery_inspector_input.setStyleSheet(self._get_input_stylesheet())
        recovery_layout.addWidget(self._recovery_inspector_input)

        recovery_manager_label = QLabel("Пароль керівника")
        recovery_manager_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        recovery_layout.addWidget(recovery_manager_label)

        self._recovery_manager_input = QLineEdit()
        self._recovery_manager_input.setEchoMode(QLineEdit.Password)
        self._recovery_manager_input.setMinimumHeight(38)
        self._recovery_manager_input.setStyleSheet(self._get_input_stylesheet())
        recovery_layout.addWidget(self._recovery_manager_input)

        recovery_button = QPushButton("Скинути")
        recovery_button.setMinimumHeight(40)
        recovery_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        recovery_button.setStyleSheet(self._get_button_stylesheet())
        recovery_button.clicked.connect(self._on_recovery_reset_clicked)
        recovery_layout.addWidget(recovery_button)

        recovery_layout.addStretch()
        tabs.addTab(recovery_tab, "Recovery-код")

        # Service tab
        service_tab = QWidget()
        service_layout = QVBoxLayout(service_tab)
        service_layout.setSpacing(12)

        service_code_label = QLabel("Сервісний код")
        service_code_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        service_layout.addWidget(service_code_label)

        self._service_code_input = QLineEdit()
        self._service_code_input.setMinimumHeight(38)
        self._service_code_input.setStyleSheet(self._get_input_stylesheet())
        service_layout.addWidget(self._service_code_input)

        service_inspector_label = QLabel("Пароль інспектора")
        service_inspector_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        service_layout.addWidget(service_inspector_label)

        self._service_inspector_input = QLineEdit()
        self._service_inspector_input.setEchoMode(QLineEdit.Password)
        self._service_inspector_input.setMinimumHeight(38)
        self._service_inspector_input.setStyleSheet(self._get_input_stylesheet())
        service_layout.addWidget(self._service_inspector_input)

        service_manager_label = QLabel("Пароль керівника")
        service_manager_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        service_layout.addWidget(service_manager_label)

        self._service_manager_input = QLineEdit()
        self._service_manager_input.setEchoMode(QLineEdit.Password)
        self._service_manager_input.setMinimumHeight(38)
        self._service_manager_input.setStyleSheet(self._get_input_stylesheet())
        service_layout.addWidget(self._service_manager_input)

        service_button = QPushButton("Скинути")
        service_button.setMinimumHeight(40)
        service_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        service_button.setStyleSheet(self._get_button_stylesheet())
        service_button.clicked.connect(self._on_service_reset_clicked)
        service_layout.addWidget(service_button)

        service_layout.addStretch()
        tabs.addTab(service_tab, "Сервісний код")

        right_layout.addWidget(tabs)

        back_button = QPushButton("Повернутися на вхід")
        back_button.setMinimumHeight(40)
        back_button.setFont(QFont("Segoe UI", 11))
        back_button.setStyleSheet(self._get_secondary_button_stylesheet())
        back_button.clicked.connect(self._on_back_to_login)
        right_layout.addWidget(back_button)

        right_card = self._create_card(right_panel)
        main_layout.addWidget(right_card, 6)

    def _on_recovery_reset_clicked(self) -> None:
        """Обробник скидання паролів через recovery-код."""
        recovery_code = self._recovery_code_input.text()
        inspector_password = self._recovery_inspector_input.text()
        manager_password = self._recovery_manager_input.text()

        if not recovery_code or not inspector_password or not manager_password:
            return

        result = reset_program_access_with_recovery_code(
            database_path=self._app_context.database_path,
            recovery_code=recovery_code,
            new_inspector_password=inspector_password,
            new_manager_password=manager_password,
        )
        self._on_finished()

    def _on_service_reset_clicked(self) -> None:
        """Обробник скидання паролів через сервісний код."""
        service_code = self._service_code_input.text()
        inspector_password = self._service_inspector_input.text()
        manager_password = self._service_manager_input.text()

        if not service_code or not inspector_password or not manager_password:
            return

        result = reset_program_access_with_service_code(
            database_path=self._app_context.database_path,
            service_code=service_code,
            new_inspector_password=inspector_password,
            new_manager_password=manager_password,
        )
        self._on_finished()

    def _create_card(self, content: QWidget) -> QFrame:
        """Створює карточку з фоном."""
        card = QFrame()
        card.setObjectName("recoveryScreenCard")
        card.setStyleSheet(
            f"QFrame#recoveryScreenCard {{ "
            f"background-color: {COLOR['bg_card']}; "
            f"border-radius: 20px; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"}}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(content)
        return card

    def _create_info_card(self, title: str, value: str) -> QFrame:
        """Створює інформаційну карточку."""
        card = QFrame()
        card.setObjectName("recoveryInfoCard")
        card.setStyleSheet(
            f"QFrame#recoveryInfoCard {{ "
            f"background-color: {COLOR['bg_panel']}; "
            f"border-radius: 12px; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"}}"
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
