"""
TopCommandBar — верхня панель команд.
Відображає назву поточного розділу, контекст та іконки керування.
TopCommandBar — top command bar showing section title and contextual controls.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.security.format_access_role_label import format_access_role_label
from osah.ui.qt.design.tokens import COLOR, FONT, SIZE, SPACING


class TopCommandBar(QWidget):
    """Верхня панель інструментів (Top bar).
    Top toolbar component containing section title and global controls.
    """

    def __init__(self, access_role: AccessRole) -> None:
        super().__init__()
        self.setProperty("role", "topbar")
        self.setFixedHeight(SIZE["top_bar_height"])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], 0, SPACING["xl"], 0)

        # Текстова частина: Заголовок і підзаголовок
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        self._title_label = QLabel()
        title_font = QFont(FONT["title_xl"][0], FONT["title_xl"][1])
        title_font.setBold(FONT["title_xl"][2])
        self._title_label.setFont(title_font)
        self._title_label.setStyleSheet(f"color: {COLOR['text_primary']};")
        text_layout.addWidget(self._title_label)

        self._subtitle_label = QLabel()
        self._subtitle_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 11px;")
        text_layout.addWidget(self._subtitle_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Права частина: Роль або статус
        role_label = QLabel(format_access_role_label(access_role))
        role_label.setProperty("pill", "info")
        role_label.setStyleSheet(
            f"background: {COLOR['role_tag_bg']}; color: {COLOR['role_tag_text']};"
            f"border-radius: 12px; padding: 4px 12px; font-weight: bold; font-size: 10px;"
        )
        layout.addWidget(role_label)
        layout.setAlignment(role_label, Qt.AlignmentFlag.AlignVCenter)

    def set_section(self, section: AppSection, alert_level: NotificationLevel | None = None) -> None:
        """Оновлює заголовок відповідно до вибраного розділу."""
        self._title_label.setText(section.value)

        # Можна потім винести підзаголовки у словник
        subtitles = {
            AppSection.DASHBOARD: "Огляд ключових показників та сигналів",
            AppSection.EMPLOYEES: "Реєстр кадрового контуру",
            AppSection.TRAININGS: "Контроль проведення інструктажів",
            AppSection.PPE: "Забезпечення засобами захисту",
            AppSection.MEDICAL: "Контроль медоглядів",
            AppSection.WORK_PERMITS: "Облік нарядів-допусків",
        }
        self._subtitle_label.setText(subtitles.get(section, "Керування розділом"))
