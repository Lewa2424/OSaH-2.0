"""
NavButton — кнопка навігаційного меню.
Підтримує стани: idle / hover / pressed / active / warning / critical.
NavButton — navigation menu button with full state support.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.nav_fill_palette import NavFillPalette
from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.qt.components.nav_fill_push_button import NavFillPushButton
from osah.ui.qt.design.ui_scale import scaled_px


class NavButton(QWidget):
    """Кнопка навігації з діаграмою фону та alert-рівнями.
    Navigation button with background diagram and alert levels.
    """

    clicked = Signal(AppSection)

    def __init__(
        self,
        section: AppSection,
        alert_level: NotificationLevel | None = None,
        fill_palette: NavFillPalette | None = None,
    ) -> None:
        super().__init__()
        self._section = section
        self._alert_level = alert_level
        self._active = False
        self._fill_palette = fill_palette

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, scaled_px(2), 0, scaled_px(2))
        layout.setSpacing(0)

        self._btn = NavFillPushButton(section.value)
        self._btn.setProperty("nav", "true")
        self._btn.setCheckable(True)
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.setFixedHeight(scaled_px(38))
        self._btn.clicked.connect(lambda: self.clicked.emit(self._section))
        layout.addWidget(self._btn)

        self._apply_visual_state()

    def set_active(self, is_active: bool) -> None:
        """Встановлює активний стан кнопки.
        Sets the active state of the button.
        """

        self._active = is_active
        self._btn.setChecked(is_active)
        self._apply_visual_state()

    def set_alert_level(self, alert_level: NotificationLevel | None) -> None:
        """Оновлює рівень сповіщення та перемальовує стилі.
        Updates the notification level and repaints styles.
        """

        if self._alert_level != alert_level:
            self._alert_level = alert_level
            self._apply_visual_state()

    def set_fill_palette(self, fill_palette: NavFillPalette | None) -> None:
        """Оновлює палітру сегментної діаграми.
        Updates the segmented diagram palette.
        """

        self._fill_palette = fill_palette
        self._apply_visual_state()

    def _apply_visual_state(self) -> None:
        if self._active:
            self._btn.setProperty("alert", "")
            self._btn.set_fill_colors(None)
            self._btn.set_problem_border(False)
        else:
            if self._alert_level == NotificationLevel.CRITICAL:
                self._btn.setProperty("alert", "critical")
            elif self._alert_level == NotificationLevel.WARNING:
                self._btn.setProperty("alert", "warning")
            else:
                self._btn.setProperty("alert", "")

            self._btn.set_fill_colors(
                self._fill_palette.colors if self._fill_palette is not None else None
            )
            self._btn.set_problem_border(self._alert_level == NotificationLevel.CRITICAL)

        self._btn.style().unpolish(self._btn)
        self._btn.style().polish(self._btn)
        self._btn.update()
