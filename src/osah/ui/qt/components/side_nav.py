"""
SideNav — ліва навігаційна панель.
Містить логотип, кнопки розділів та footer.
SideNav — left navigation panel containing logo, buttons and footer.
"""
from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.qt.components.nav_button import NavButton
from osah.ui.qt.design.tokens import COLOR, FONT, SIZE, SPACING


class SideNav(QWidget):
    """Ліва навігаційна панель (Sidebar)."""

    section_selected = Signal(AppSection)

    def __init__(
        self,
        sections: tuple[AppSection, ...],
        access_role: AccessRole,
        section_levels: dict[AppSection, NotificationLevel],
    ) -> None:
        super().__init__()
        self.setProperty("role", "sidenav")
        self.setFixedWidth(SIZE["nav_width"])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["xl"], SPACING["lg"], SPACING["xl"])
        layout.setSpacing(SPACING["sm"])

        # ---- Логотип ----
        logo = QLabel("OSaH 2.0 🚀")
        logo_font = QFont(FONT["title_xl"][0], 18)
        logo_font.setBold(True)
        logo.setFont(logo_font)
        logo.setStyleSheet(f"color: {COLOR['accent']};")
        layout.addWidget(logo)

        desc = QLabel("Локальний пульт інспектора з охорони праці.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 10px;")
        layout.addWidget(desc)

        layout.addSpacing(SPACING["lg"])

        # ---- Кнопки навігації ----
        self._buttons: dict[AppSection, NavButton] = {}

        for section in sections:
            # Розділювач перед другорядною групою
            if section == AppSection.CONTRACTORS:
                sep = QFrame()
                sep.setFixedHeight(1)
                sep.setStyleSheet(f"background: {COLOR['border_soft']}; margin: 8px 0;")
                layout.addWidget(sep)

            btn = NavButton(section, section_levels.get(section))
            btn.clicked.connect(self._on_button_clicked)
            layout.addWidget(btn)
            self._buttons[section] = btn

        layout.addStretch()

        # ---- Footer ----
        footer = QLabel("Система працює автономно.")
        footer.setWordWrap(True)
        footer.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 10px;")
        layout.addWidget(footer)

    def _on_button_clicked(self, section: AppSection) -> None:
        self.set_active_section(section)
        self.section_selected.emit(section)

    def set_active_section(self, active_section: AppSection) -> None:
        """Оновлює стан кнопок: підсвічує активну, скидає інші."""
        for section, btn in self._buttons.items():
            btn.set_active(section == active_section)
