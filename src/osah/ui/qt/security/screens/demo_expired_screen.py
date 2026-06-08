"""Екран завершення демонстраційного періоду / Demo period expired screen."""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.infrastructure.config.support_contacts import SUPPORT_EMAIL, SUPPORT_PHONE
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.security.screens.security_background_shell import SecurityBackgroundShell


class DemoExpiredScreen(QWidget):
    """Блокує доступ після завершення 48-годинного demo-only періоду."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("demoExpiredRoot")
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

        card = QWidget()
        card.setMaximumWidth(760)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(SPACING["md"])

        title = QLabel("Демонстраційний період завершено")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR['text_primary']};")
        title.setWordWrap(True)
        card_layout.addWidget(title)

        description = QLabel(
            "Термін демонстраційної версії ClearWork (48 годин) вичерпано. "
            "Ця збірка призначена лише для ознайомлення з можливостями програми "
            "і не підходить для виробничої експлуатації."
        )
        description.setFont(QFont("Segoe UI", 12))
        description.setStyleSheet(f"color: {COLOR['text_secondary']};")
        description.setWordWrap(True)
        card_layout.addWidget(description)

        contacts = QLabel(
            "Щоб отримати повну версію ClearWork для роботи на підприємстві, зверніться до розробника:\n"
            f"Email: {SUPPORT_EMAIL}\n"
            f"Телефон: {SUPPORT_PHONE}"
        )
        contacts.setFont(QFont("Segoe UI", 12))
        contacts.setStyleSheet(f"color: {COLOR['text_primary']};")
        contacts.setWordWrap(True)
        card_layout.addWidget(contacts)

        shell_layout.addWidget(card, 0)
        shell_layout.addStretch(2)
