"""
Qt Initial Setup Screen - екран першого налаштування безпеки.
Qt Initial Setup Screen - экран первичной настройки безопасности.
"""
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PySide6.QtGui import QFont

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.load_security_profile import load_security_profile
from osah.application.services.security.configure_program_access import configure_program_access
from osah.ui.qt.design.tokens import COLOR


class InitialSetupScreen(QWidget):
    """Екран першого налаштування паролів і recovery-механіки.
    Экран первичной настройки паролей и recovery-механики.
    """

    def __init__(
        self,
        application_context: ApplicationContext,
        on_configured: Callable[[], None],
    ) -> None:
        """
        Ініціалізує екран.
        Инициализирует экран.
        """
        super().__init__()
        self._app_context = application_context
        self._on_configured = on_configured
        self._security_profile = load_security_profile(application_context.database_path)

        self.setStyleSheet(f"background-color: {COLOR['bg_app']};")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Будує інтерфейс екрана."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(14)

        # ---- Ліва інформаційна панель ----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(28, 28, 28, 28)
        left_layout.setSpacing(20)

        # Заголовок
        title = QLabel("Первинне налаштування доступу")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        left_layout.addWidget(title)

        # Опис
        description = QLabel(
            "На першому запуску потрібно зафіксувати окремі паролі для інспектора і керівника. "
            "Після збереження система створить recovery-файл і ввімкне локальний security-контур."
        )
        description.setFont(QFont("Segoe UI", 10))
        description.setStyleSheet(f"color: {COLOR['text_muted']};")
        description.setWordWrap(True)
        left_layout.addWidget(description)

        # Карточка з ID установки
        info_card = self._create_info_card(
            "ID установки",
            self._security_profile.installation_id
        )
        left_layout.addWidget(info_card)

        # Примітка про security
        security_note = QLabel(
            "Паролі не зберігаються у відкритому вигляді, а recovery-файл потрібно тримати окремо від робочого ПК."
        )
        security_note.setFont(QFont("Segoe UI", 10, QFont.Bold))
        security_note.setStyleSheet(f"color: {COLOR['text_muted']};")
        security_note.setWordWrap(True)
        left_layout.addWidget(security_note)

        left_layout.addStretch()

        left_card = self._create_card(left_panel)
        main_layout.addWidget(left_card, 5)

        # ---- Права форма ----
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(28, 28, 28, 28)
        right_layout.setSpacing(18)

        form_title = QLabel("Параметри першого запуску")
        form_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        form_title.setStyleSheet(f"color: {COLOR['text_primary']};")
        right_layout.addWidget(form_title)

        form_description = QLabel(
            "Задайте окремі локальні паролі для повного та read-only доступу."
        )
        form_description.setFont(QFont("Segoe UI", 10))
        form_description.setStyleSheet(f"color: {COLOR['text_muted']};")
        form_description.setWordWrap(True)
        right_layout.addWidget(form_description)

        # Inspector password
        inspector_label = QLabel("Пароль інспектора")
        inspector_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        inspector_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        right_layout.addWidget(inspector_label)

        self._inspector_input = QLineEdit()
        self._inspector_input.setEchoMode(QLineEdit.Password)
        self._inspector_input.setMinimumHeight(38)
        self._inspector_input.setStyleSheet(self._get_input_stylesheet())
        right_layout.addWidget(self._inspector_input)

        # Manager password
        manager_label = QLabel("Пароль керівника")
        manager_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        manager_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        right_layout.addWidget(manager_label)

        self._manager_input = QLineEdit()
        self._manager_input.setEchoMode(QLineEdit.Password)
        self._manager_input.setMinimumHeight(38)
        self._manager_input.setStyleSheet(self._get_input_stylesheet())
        right_layout.addWidget(self._manager_input)

        right_layout.addStretch()

        # Save button
        save_button = QPushButton("Зберегти параметри")
        save_button.setMinimumHeight(40)
        save_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        save_button.setStyleSheet(self._get_button_stylesheet())
        save_button.clicked.connect(self._on_save_clicked)
        right_layout.addWidget(save_button)

        self.setTabOrder(self._inspector_input, self._manager_input)
        self.setTabOrder(self._manager_input, save_button)

        right_card = self._create_card(right_panel)
        main_layout.addWidget(right_card, 6)

    def _on_save_clicked(self) -> None:
        """Обробник натиснення кнопки збереження."""
        inspector_password = self._inspector_input.text()
        manager_password = self._manager_input.text()

        if not inspector_password or not manager_password:
            # TODO: Показати повідомлення про помилку
            return

        # Зберегти конфігурацію
        configure_program_access(
            database_path=self._app_context.database_path,
            inspector_password=inspector_password,
            manager_password=manager_password,
        )

        self._on_configured()

    def _create_card(self, content: QWidget) -> QFrame:
        """Створює карточку з фоном."""
        card = QFrame()
        card.setObjectName("initialSetupCard")
        card.setStyleSheet(
            f"QFrame#initialSetupCard {{ "
            f"background-color: {COLOR['bg_card']}; "
            f"border-radius: 20px; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"}}"
        )
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(content)
        
        return card

    def _create_info_card(self, title: str, value: str) -> QFrame:
        """Створює інформаційну карточку."""
        card = QFrame()
        card.setObjectName("initialSetupInfoCard")
        card.setStyleSheet(
            f"QFrame#initialSetupInfoCard {{ "
            f"background-color: {COLOR['bg_panel']}; "
            f"border-radius: 12px; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"}}"
        )
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLOR['text_muted']};")
        card_layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLOR['text_primary']};")
        card_layout.addWidget(value_label)

        return card

    def _get_input_stylesheet(self) -> str:
        """Повертає stylesheet для input-полів."""
        return (
            f"QLineEdit {{\n"
            f"    background-color: {COLOR['bg_card']};\n"
            f"    color: {COLOR['text_primary']};\n"
            f"    border: 1px solid {COLOR['border_soft']};\n"
            f"    border-radius: 12px;\n"
            f"    padding: 0 8px;\n"
            f"    font: 11pt 'Segoe UI';\n"
            f"}}\n"
            f"QLineEdit:focus {{\n"
            f"    border: 2px solid {COLOR['accent']};\n"
            f"}}"
        )

    def _get_button_stylesheet(self) -> str:
        """Повертає stylesheet для кнопок."""
        return (
            f"QPushButton {{\n"
            f"    background-color: {COLOR['accent']};\n"
            f"    color: {COLOR['accent_text']};\n"
            f"    border: 1px solid {COLOR['accent']};\n"
            f"    border-radius: 15px;\n"
            f"    padding: 0;\n"
            f"    font: bold 11pt 'Segoe UI';\n"
            f"}}\n"
            f"QPushButton:hover {{\n"
            f"    background-color: {COLOR['accent_hover']};\n"
            f"    border: 1px solid {COLOR['accent_hover']};\n"
            f"}}\n"
            f"QPushButton:pressed {{\n"
            f"    background-color: {COLOR['accent']};\n"
            f"}}"
        )
