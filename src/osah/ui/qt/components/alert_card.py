"""
Alert card for dashboard notifications.
"""

from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.qt.design.tokens import ANIMATION, COLOR, RADIUS, SPACING


def _resolve_level_colors(level: NotificationLevel) -> tuple[str, str, str]:
    """###### КОЛЬОРИ РІВНЯ / LEVEL COLORS ######"""

    if level == NotificationLevel.CRITICAL:
        return COLOR["critical"], COLOR["critical"], COLOR["text_on_accent"]
    if level == NotificationLevel.WARNING:
        return COLOR["warning"], COLOR["warning"], COLOR["text_on_accent"]
    return COLOR["accent"], COLOR["accent"], COLOR["text_on_accent"]


def _level_label(level: NotificationLevel) -> str:
    """###### ПІДПИС РІВНЯ / LEVEL LABEL ######"""

    if level == NotificationLevel.CRITICAL:
        return "Критично"
    if level == NotificationLevel.WARNING:
        return "Увага"
    return "Інфо"


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

        bar_color, badge_bg, badge_text = _resolve_level_colors(notification.notification_level)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("alertCardFrame")
        outer.addWidget(card)
        self._card = card
        self._apply_card_style(self._base_background, self._base_border)

        h = QHBoxLayout(card)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setStyleSheet(
            f"background: {bar_color};"
            f"border-top-left-radius: {RADIUS['md']}px;"
            f"border-bottom-left-radius: {RADIUS['md']}px;"
            "border-top-right-radius: 0px;"
            "border-bottom-right-radius: 0px;"
        )
        h.addWidget(bar)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        v = QVBoxLayout(body)
        v.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        v.setSpacing(6)
        h.addWidget(body)

        pill_row = QWidget()
        pill_row.setStyleSheet("background: transparent;")
        pill_h = QHBoxLayout(pill_row)
        pill_h.setContentsMargins(0, 0, 0, 0)
        pill_h.setSpacing(0)

        badge = QLabel(_level_label(notification.notification_level))
        badge.setProperty("pill", notification.notification_level.value.lower())
        badge.setStyleSheet(
            f"background: {badge_bg}; color: {badge_text};"
            "border-radius: 9px; padding: 2px 10px;"
            "font-size: 9px; font-weight: bold;"
        )
        pill_h.addWidget(badge)
        pill_h.addStretch()
        v.addWidget(pill_row)

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
        self._apply_card_style(background, border)

    def _apply_card_style(self, background: str, border: str) -> None:
        """###### СТИЛЬ КАРТКИ / CARD STYLE ######"""

        if self._card is None:
            return
        self._card.setStyleSheet(
            f"""
            QFrame#alertCardFrame {{
                background: {background};
                border: 1px solid {border};
                border-radius: {RADIUS['md']}px;
            }}
            """
        )
