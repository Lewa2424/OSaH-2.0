"""
NavButton — кнопка навігаційного меню.
Підтримує стани: idle / hover / pressed / active / warning / critical.
NavButton — navigation menu button with full state support.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.qt.design.tokens import COLOR


class NavButton(QWidget):
    """Кнопка навігації з підтримкою alert-рівній і станів.
    Navigation button with alert-level and state support.
    """

    clicked = Signal(AppSection)

    def __init__(self, section: AppSection, alert_level: NotificationLevel | None = None) -> None:
        super().__init__()
        self._section = section
        self._alert_level = alert_level
        self._active = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(0)

        # Кнопка / Button
        self._btn = QPushButton(section.value)
        self._btn.setProperty("nav", "true")
        self._btn.setCheckable(True)
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.setFixedHeight(38)
        self._btn.clicked.connect(lambda: self.clicked.emit(self._section))
        layout.addWidget(self._btn)

        self._apply_alert_style()

    # ──────────────────────────────────────────────────────────────
    def set_active(self, is_active: bool) -> None:
        """Встановлює активний стан кнопки.
        Sets the active state of the button.
        """
        self._active = is_active
        self._btn.setChecked(is_active)
        if is_active:
            # Активна кнопка не показує alert-стиль
            self._btn.setProperty("alert", "")
        else:
            self._apply_alert_style()
        # Примушуємо Qt перечитати динамічне QSS-властивість
        self._btn.style().unpolish(self._btn)
        self._btn.style().polish(self._btn)

    # ──────────────────────────────────────────────────────────────
    def _apply_alert_style(self) -> None:
        if self._alert_level == NotificationLevel.CRITICAL:
            self._btn.setProperty("alert", "critical")
        elif self._alert_level == NotificationLevel.WARNING:
            self._btn.setProperty("alert", "warning")
        else:
            self._btn.setProperty("alert", "")
            
        self._btn.style().unpolish(self._btn)
        self._btn.style().polish(self._btn)

    def set_alert_level(self, alert_level: NotificationLevel | None) -> None:
        """Оновлює рівень сповіщення та перемальовує стилі."""
        if self._alert_level != alert_level:
            self._alert_level = alert_level
            self._apply_alert_style()
