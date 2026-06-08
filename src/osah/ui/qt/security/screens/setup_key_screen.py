"""Екран активації ключа установки ClearWork / ClearWork setup key activation screen."""

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.activate_setup_key import activate_setup_key
from osah.application.services.security.load_security_profile import load_security_profile
from osah.domain.services.setup_key.verify_setup_key_document import SetupKeyVerificationError
from osah.infrastructure.config.support_contacts import SUPPORT_EMAIL, SUPPORT_PHONE
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.security.screens.security_background_shell import SecurityBackgroundShell
from osah.ui.qt.security.screens.setup_key_request_dialog import SetupKeyRequestDialog


class SetupKeyScreen(QWidget):
    """Екран введення ключа установки перед первинним налаштуванням паролів."""

    def __init__(
        self,
        application_context: ApplicationContext,
        on_activated: Callable[[], None],
    ) -> None:
        super().__init__()
        self._app_context = application_context
        self._on_activated = on_activated
        self._security_profile = load_security_profile(application_context.database_path)
        self.setObjectName("setupKeyRoot")
        self._setup_ui()

    def _setup_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        shell = SecurityBackgroundShell()
        root_layout.addWidget(shell)

        shell_layout = shell.content_layout()
        shell_layout.setContentsMargins(44, 36, 44, 36)
        shell_layout.setSpacing(SPACING["lg"])
        shell_layout.addStretch(1)

        content = QWidget()
        content.setMinimumWidth(960)
        content.setMaximumWidth(1120)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING["lg"])
        content_layout.addWidget(self._build_activation_card())
        content_layout.addWidget(self._build_service_strip())
        shell_layout.addWidget(content, 0, Qt.AlignmentFlag.AlignHCenter)
        shell_layout.addStretch(2)

    def _build_activation_card(self) -> QFrame:
        card = self._create_shell_card("setupKeyCard")
        card.setMinimumHeight(360)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Активація ClearWork")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        layout.addWidget(title)

        description = QLabel(
            "Вставте ключ установки, який ви отримали від розробника. "
            "Якщо ключа ще немає, надішліть ID установки на "
            f"{SUPPORT_EMAIL} або {SUPPORT_PHONE}."
        )
        description.setFont(QFont("Segoe UI", 12))
        description.setStyleSheet(f"color: {COLOR['text_secondary']};")
        description.setWordWrap(True)
        layout.addWidget(description)

        self._key_input = QPlainTextEdit()
        self._key_input.setPlaceholderText("ВСТАВТЕ КЛЮЧ УСТАНОВКИ (CW-...)")
        self._key_input.setMinimumHeight(110)
        self._key_input.setStyleSheet(self._get_text_area_stylesheet())
        layout.addWidget(self._key_input)

        self._feedback_label = QLabel("")
        self._feedback_label.setFont(QFont("Segoe UI", 11))
        self._feedback_label.setStyleSheet(f"color: {COLOR['danger']};")
        self._feedback_label.setWordWrap(True)
        layout.addWidget(self._feedback_label)

        activate_button = QPushButton("Активувати")
        activate_button.setMinimumHeight(52)
        activate_button.setStyleSheet(self._get_button_stylesheet())
        activate_button.clicked.connect(self._on_activate_clicked)
        layout.addWidget(activate_button)

        request_button = QPushButton("Сформувати запит на ключ установки")
        request_button.setMinimumHeight(48)
        request_button.setStyleSheet(self._get_secondary_button_stylesheet())
        request_button.clicked.connect(self._on_request_report_clicked)
        layout.addWidget(request_button)
        return card

    def _build_service_strip(self) -> QFrame:
        strip = self._create_shell_card("setupKeyServiceStrip")
        strip.setMinimumHeight(110)
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(SPACING["md"])

        text_panel = QWidget()
        text_layout = QVBoxLayout(text_panel)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)

        title = QLabel("Локальна установка")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        text_layout.addWidget(title)

        description = QLabel(
            "ID установки потрібен для отримання ключа. Після активації ключ більше не запитується."
        )
        description.setFont(QFont("Segoe UI", 10))
        description.setStyleSheet(f"color: {COLOR['text_secondary']};")
        description.setWordWrap(True)
        text_layout.addWidget(description)
        text_layout.addStretch()
        layout.addWidget(text_panel, 2)

        id_panel = QWidget()
        id_layout = QVBoxLayout(id_panel)
        id_layout.setContentsMargins(0, 0, 0, 0)
        id_layout.setSpacing(SPACING["xs"])
        id_layout.addWidget(
            self._create_info_card("ID установки", self._security_profile.installation_id),
        )

        copy_button = QPushButton("Скопіювати ID")
        copy_button.setMinimumHeight(36)
        copy_button.setStyleSheet(self._get_secondary_button_stylesheet())
        copy_button.clicked.connect(self._on_copy_installation_id_clicked)
        id_layout.addWidget(copy_button)
        layout.addWidget(id_panel, 3)
        return strip

    def _on_copy_installation_id_clicked(self) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self._security_profile.installation_id)
        self._feedback_label.setStyleSheet(f"color: {COLOR['success']};")
        self._feedback_label.setText("ID установки скопійовано в буфер обміну.")

    def _on_request_report_clicked(self) -> None:
        dialog = SetupKeyRequestDialog(
            self,
            installation_id=self._security_profile.installation_id,
            data_directory=self._app_context.database_path.parent,
        )
        dialog.exec()

    def _on_activate_clicked(self) -> None:
        paste_token = self._key_input.toPlainText().strip()
        if not paste_token:
            self._feedback_label.setText("Вставте ключ установки.")
            return

        try:
            activate_setup_key(self._app_context.database_path, paste_token)
        except SetupKeyVerificationError as error:
            self._feedback_label.setText(str(error))
            return
        except ValueError as error:
            self._feedback_label.setText(str(error))
            return
        except Exception:
            self._feedback_label.setText("Не вдалося активувати ключ установки.")
            return

        self._feedback_label.setStyleSheet(f"color: {COLOR['success']};")
        self._feedback_label.setText("Ключ установки прийнято.")
        self._on_activated()

    def _create_shell_card(self, object_name: str) -> QFrame:
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
        card = QFrame()
        card.setObjectName("setupKeyInfoCard")
        card.setStyleSheet(
            f"QFrame#setupKeyInfoCard {{ "
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

    def _get_text_area_stylesheet(self) -> str:
        return (
            f"QPlainTextEdit {{ "
            f"background: {COLOR['input_bg']}; "
            f"color: {COLOR['input_text']}; "
            f"border: 1px solid {COLOR['input_border']}; "
            f"border-radius: {RADIUS['md']}px; "
            f"padding: 12px 16px; "
            f"font: 12pt 'Segoe UI'; "
            f"}} "
            f"QPlainTextEdit:focus {{ border: 2px solid {COLOR['input_border_focus']}; }}"
        )

    def _get_button_stylesheet(self) -> str:
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
        return (
            f"QPushButton {{ "
            f"background: {COLOR['bg_panel']}; "
            f"color: {COLOR['text_primary']}; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['md']}px; "
            f"font: 11pt 'Segoe UI'; "
            f"}} "
            f"QPushButton:hover {{ background: {COLOR['bg_card']}; }}"
        )
