"""
Dashboard metric card component.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, FONT, RADIUS, SPACING


class MetricCard(QWidget):
    """Compact KPI card for the dashboard top row."""

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str,
        accent_color: str,
    ) -> None:
        super().__init__()

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("metricCard")
        card.setMinimumHeight(88)
        card.setStyleSheet(
            f"QFrame#metricCard {{ "
            f"background: {COLOR['metric_card_bg']}; "
            f"border: 2px solid {accent_color}; "
            f"border-radius: {RADIUS['xl']}px; "
            f"}}"
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 16))
        card.setGraphicsEffect(shadow)

        outer_layout.addWidget(card)

        content_layout = QVBoxLayout(card)
        content_layout.setContentsMargins(
            SPACING["md"],
            SPACING["md"],
            SPACING["md"],
            SPACING["md"],
        )
        content_layout.setSpacing(3)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"color: {COLOR['metric_card_label']};"
            "font-size: 11px;"
            "font-weight: 700;"
        )
        content_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_font = QFont(FONT["metric"][0], FONT["metric"][1] + 2)
        value_font.setBold(FONT["metric"][2])
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {accent_color};")
        content_layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(
            f"color: {COLOR['text_secondary']};"
            "font-size: 10px;"
            "font-weight: 400;"
        )
        content_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
