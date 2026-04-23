"""
Alert card for dashboard notifications.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_level import NotificationLevel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


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


class AlertCard(QWidget):
    """Dashboard active notification card."""

    clicked = Signal()

    def __init__(self, notification: NotificationItem) -> None:
        super().__init__()
        self._notification = notification
        if notification.employee_personnel_number:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        bar_color, badge_bg, badge_text = _resolve_level_colors(notification.notification_level)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setProperty("inset", "true")
        outer.addWidget(card)

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

    def mousePressEvent(self, event) -> None:
        """###### КЛІК ПО СПОВІЩЕННЮ / NOTIFICATION CLICK ######"""

        if self._notification.employee_personnel_number:
            self.clicked.emit()
        super().mousePressEvent(event)
