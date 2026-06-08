"""
Alert card for dashboard notifications.
"""

from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.qt.design.tokens import ANIMATION, COLOR, RADIUS, SPACING


_LEVEL_STYLE: dict[NotificationLevel, tuple[str, str, str]] = {
    NotificationLevel.CRITICAL: ("Критично", COLOR["critical_subtle"], COLOR["critical"]),
    NotificationLevel.WARNING: ("Увага", COLOR["warning_subtle"], COLOR["warning"]),
    NotificationLevel.INFO: ("Інфо", COLOR["accent_subtle"], COLOR["accent"]),
}


def _resolve_level_style(level: NotificationLevel) -> tuple[str, str, str]:
    """###### СТИЛЬ РІВНЯ / LEVEL STYLE ######"""

    return _LEVEL_STYLE.get(level, _LEVEL_STYLE[NotificationLevel.INFO])


def _mix_hex_color(start_hex: str, end_hex: str, progress: float) -> str:
    """###### ЗМІШУВАННЯ КОЛЬОРІВ / MIX HEX COLORS ######"""

    start = QColor(start_hex)
    end = QColor(end_hex)
    ratio = max(0.0, min(1.0, progress))
    red = round(start.red() + (end.red() - start.red()) * ratio)
    green = round(start.green() + (end.green() - start.green()) * ratio)
    blue = round(start.blue() + (end.blue() - start.blue()) * ratio)
    return QColor(red, green, blue).name()


class AlertCard(QWidget):
    """Dashboard active notification card."""

    clicked = Signal()

    def __init__(self, notification: NotificationItem) -> None:
        super().__init__()
        self._notification = notification
        self._is_interactive = bool(notification.employee_personnel_number)
        self._base_background = COLOR["mini_card_bg"]
        self._hover_background = COLOR["mini_card_hover_bg"]
        self._base_border = COLOR["mini_card_border"]
        self._hover_border = COLOR["border_default"]
        self._card: QFrame | None = None
        self._hover_animation: QVariantAnimation | None = None
        if self._is_interactive:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        level_label, badge_bg, accent_color = _resolve_level_style(notification.notification_level)
        self._accent_color = accent_color

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("alertCardFrame")
        outer.addWidget(card)
        self._card = card
        self._apply_card_style(self._base_background, self._base_border, self._accent_color)

        v = QVBoxLayout(card)
        v.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        v.setSpacing(6)

        badge = QLabel(level_label)
        badge.setProperty("pill", notification.notification_level.value.lower())
        badge.setStyleSheet(
            f"background: {badge_bg}; color: {accent_color};"
            f"border: 1px solid {accent_color};"
            "border-radius: 10px; padding: 3px 10px;"
            "font-size: 10px; font-weight: 700;"
        )
        v.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        title = QLabel(notification.title_text)
        title.setProperty("role", "alert_title")
        v.addWidget(title)

        subject = notification.employee_full_name or notification.employee_personnel_number or "Система"
        body_text = QLabel(f"{subject}: {notification.message_text}")
        body_text.setProperty("role", "alert_body")
        body_text.setWordWrap(True)
        v.addWidget(body_text)

        if self._is_interactive:
            self._hover_animation = self._build_hover_animation()

    def mousePressEvent(self, event) -> None:
        """###### КЛІК ПО СПОВІЩЕННЮ / NOTIFICATION CLICK ######"""

        if self._notification.employee_personnel_number:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        """###### НАВЕДЕННЯ НА КАРТКУ / CARD HOVER ENTER ######"""

        if self._is_interactive:
            self._start_hover_animation(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """###### ВИХІД З HOVER / CARD HOVER LEAVE ######"""

        if self._is_interactive:
            self._start_hover_animation(0.0)
        super().leaveEvent(event)

    def _build_hover_animation(self) -> QVariantAnimation:
        """###### АНІМАЦІЯ HOVER / HOVER ANIMATION ######"""

        animation = QVariantAnimation(self)
        animation.setDuration(ANIMATION["fast"])
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.valueChanged.connect(self._apply_hover_progress)
        return animation

    def _start_hover_animation(self, target_progress: float) -> None:
        """###### ЗАПУСК HOVER-АНІМАЦІЇ / START HOVER ANIMATION ######"""

        if self._hover_animation is None:
            return
        current_progress = float(self._hover_animation.currentValue() or 0.0)
        self._hover_animation.stop()
        self._hover_animation.setStartValue(current_progress)
        self._hover_animation.setEndValue(target_progress)
        self._hover_animation.start()

    def _apply_hover_progress(self, progress: object) -> None:
        """###### ЗАСТОСУВАННЯ HOVER-СТАНУ / APPLY HOVER STATE ######"""

        ratio = float(progress)
        background = _mix_hex_color(self._base_background, self._hover_background, ratio)
        border = _mix_hex_color(self._base_border, self._hover_border, ratio)
        self._apply_card_style(background, border, self._accent_color)

    def _apply_card_style(self, background: str, border: str, accent: str) -> None:
        """###### СТИЛЬ КАРТКИ / CARD STYLE ######"""

        if self._card is None:
            return
        self._card.setStyleSheet(
            f"""
            QFrame#alertCardFrame {{
                background: {background};
                border: 1px solid {border};
                border-left: 4px solid {accent};
                border-radius: {RADIUS['md']}px;
            }}
            """
        )
